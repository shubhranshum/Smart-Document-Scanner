from typing import Tuple, List, Optional, Dict, Any
import numpy as np
import cv2
from fastapi import HTTPException, status
from app.config import settings

def validate_quadrilateral(pts: np.ndarray) -> Tuple[bool, Optional[str]]:
    """
    Validates whether four 2D points form a non-degenerate, convex quadrilateral.
    pts: (4, 2) float array
    """
    if pts is None or len(pts) != 4:
        return False, "Expected exactly 4 points."

    # Check for NaN / Inf
    if not np.isfinite(pts).all():
        return False, "Coordinates contain invalid numeric values (NaN or Inf)."

    # Check distinct points (min distance between any pair)
    for i in range(4):
        for j in range(i + 1, 4):
            dist = np.linalg.norm(pts[i] - pts[j])
            if dist < 5.0:
                return False, f"Points {i} and {j} are too close to each other (distance < 5px)."

    # Check edge lengths
    for i in range(4):
        p1 = pts[i]
        p2 = pts[(i + 1) % 4]
        edge_len = np.linalg.norm(p2 - p1)
        if edge_len < 10.0:
            return False, f"Edge between point {i} and {(i + 1) % 4} is too short (< 10px)."

    # Check convexity and no self-intersection via edge cross-products
    # Cross product of (v1 x v2) must all share the same non-zero sign
    cross_products = []
    for i in range(4):
        p_prev = pts[(i - 1) % 4]
        p_curr = pts[i]
        p_next = pts[(i + 1) % 4]
        v1 = p_curr - p_prev
        v2 = p_next - p_curr
        cp = v1[0] * v2[1] - v1[1] * v2[0]
        cross_products.append(cp)

    signs = [np.sign(cp) for cp in cross_products if abs(cp) > 1e-5]
    if len(signs) < 4:
        return False, "Collinear or degenerate edges detected."

    if not (all(s > 0 for s in signs) or all(s < 0 for s in signs)):
        return False, "Polygon is self-intersecting or non-convex."

    # Check polygon area
    area = cv2.contourArea(pts.astype(np.float32))
    if area < 100.0:
        return False, "Quadrilateral area is too small (< 100 px^2)."

    return True, None

def order_corners(pts: np.ndarray) -> np.ndarray:
    """
    Orders 4 quadrilateral corners deterministically in clockwise order:
    [Top-Left, Top-Right, Bottom-Right, Bottom-Left].
    
    Uses centroid angular sorting followed by top-left identification
    and winding direction normalization.
    """
    pts = np.asarray(pts, dtype=np.float32).reshape((4, 2))

    # 1. Compute centroid
    cx = np.mean(pts[:, 0])
    cy = np.mean(pts[:, 1])

    # 2. Sort points by polar angle relative to centroid
    angles = np.arctan2(pts[:, 1] - cy, pts[:, 0] - cx)
    sort_idx = np.argsort(angles)
    ordered_pts = pts[sort_idx]

    # 3. Determine winding direction: compute cross product of consecutive edge vectors
    v1 = ordered_pts[1] - ordered_pts[0]
    v2 = ordered_pts[2] - ordered_pts[1]
    cross = v1[0] * v2[1] - v1[1] * v2[0]

    # If counter-clockwise (cross > 0 in standard screen coordinates where y is down),
    # reverse to make it clockwise: TL -> TR -> BR -> BL
    if cross < 0:
        # Currently counter-clockwise in screen coordinates
        ordered_pts = ordered_pts[::-1]

    # 4. Now the polygon is strictly clockwise cyclic.
    # Identify the Top-Left corner: minimize (x + y), or distance to origin (0, 0)
    scores = ordered_pts[:, 0] + ordered_pts[:, 1]
    tl_idx = np.argmin(scores)

    # Roll array so top-left is at index 0
    final_ordered = np.roll(ordered_pts, -tl_idx, axis=0)

    # Secondary check: ensure index 1 is Top-Right (x should be larger than TL)
    # and index 3 is Bottom-Left (y should be larger than TL)
    # If not, use standard fallback sum/diff
    tl, tr, br, bl = final_ordered
    if not (tr[0] > tl[0] or bl[1] > tl[1]):
        # Fallback sum/difference method
        s = pts.sum(axis=1)
        tl_fallback = pts[np.argmin(s)]
        br_fallback = pts[np.argmax(s)]

        diff = np.diff(pts, axis=1)
        tr_fallback = pts[np.argmin(diff)]
        bl_fallback = pts[np.argmax(diff)]
        final_ordered = np.array([tl_fallback, tr_fallback, br_fallback, bl_fallback], dtype=np.float32)

    return final_ordered

def compute_perspective_transform_dimensions(ordered_corners: np.ndarray) -> Tuple[int, int]:
    """
    Computes output rectangle (width, height) from the 4 corners:
    TL: ordered_corners[0]
    TR: ordered_corners[1]
    BR: ordered_corners[2]
    BL: ordered_corners[3]
    """
    tl, tr, br, bl = ordered_corners

    # Width: max of top edge and bottom edge
    width_top = np.linalg.norm(tr - tl)
    width_bottom = np.linalg.norm(br - bl)
    max_width = int(round(max(width_top, width_bottom)))

    # Height: max of left edge and right edge
    height_left = np.linalg.norm(bl - tl)
    height_right = np.linalg.norm(br - tr)
    max_height = int(round(max(height_left, height_right)))

    # Prevent 0 or negative dimensions
    max_width = max(10, max_width)
    max_height = max(10, max_height)

    # Enforce max pixel safety limit to avoid OOM
    total_pixels = max_width * max_height
    if total_pixels > settings.max_output_pixels:
        ratio = (settings.max_output_pixels / total_pixels) ** 0.5
        max_width = max(10, int(round(max_width * ratio)))
        max_height = max(10, int(round(max_height * ratio)))

    return max_width, max_height

def apply_perspective_correction(
    image: np.ndarray,
    corners: np.ndarray,
    target_width: Optional[int] = None,
    target_height: Optional[int] = None
) -> Tuple[np.ndarray, int, int, np.ndarray]:
    """
    Performs perspective warping on the input image given 4 corners.
    Validates corners, orders them, computes destination dimensions,
    and applies cv2.warpPerspective.
    
    Returns: (corrected_image, output_width, output_height, homography_matrix)
    """
    corners = np.asarray(corners, dtype=np.float32)
    is_valid, error_msg = validate_quadrilateral(corners)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid quadrilateral coordinates: {error_msg}"
        )

    ordered_pts = order_corners(corners)

    if target_width is not None and target_height is not None:
        out_w = max(10, int(target_width))
        out_h = max(10, int(target_height))
    else:
        out_w, out_h = compute_perspective_transform_dimensions(ordered_pts)

    dst_pts = np.array([
        [0, 0],
        [out_w - 1, 0],
        [out_w - 1, out_h - 1],
        [0, out_h - 1]
    ], dtype=np.float32)

    # Compute 3x3 homography matrix
    M = cv2.getPerspectiveTransform(ordered_pts, dst_pts)

    # Warp perspective using bicubic interpolation for clean text and edges
    warped = cv2.warpPerspective(
        image,
        M,
        (out_w, out_h),
        flags=cv2.INTER_CUBIC,
        borderMode=cv2.BORDER_REPLICATE
    )

    return warped, out_w, out_h, M
