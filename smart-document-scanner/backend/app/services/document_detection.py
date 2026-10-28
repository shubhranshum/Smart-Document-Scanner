from typing import Tuple, List, Optional, Dict, Any
from itertools import combinations
import cv2
import numpy as np
from app.config import settings
from app.services.preprocessing import resize_for_detection, preprocess_image
from app.services.perspective import order_corners, validate_quadrilateral

def extract_4_corners_from_polygon(pts: np.ndarray) -> Optional[np.ndarray]:
    """
    Given a convex polygon with N vertices (where N >= 4), extracts the 4 vertices
    that best form the document quadrilateral.
    Gracefully handles rounded corners, folds, or lens curvature via:
      1. Rotated coordinate extrema along the minimum-area rectangle orientation.
      2. Direct coordinate extrema (x + y, x - y).
      3. Douglas-Peucker area-maximizing vertex subset selection.
    """
    pts = pts.reshape(-1, 2).astype(np.float32)
    N = len(pts)

    if N < 4:
        return None
    if N == 4:
        is_valid, _ = validate_quadrilateral(pts)
        return pts if is_valid else None

    # Method 1: Rotated Extrema aligned to contour principal axis (fastest & most accurate for rounded corners)
    try:
        rect = cv2.minAreaRect(pts)
        box_angle = np.deg2rad(rect[2])
        cos_a, sin_a = np.cos(-box_angle), np.sin(-box_angle)
        R_align = np.array([[cos_a, -sin_a], [sin_a, cos_a]])
        aligned = (pts - rect[0]) @ R_align.T

        s = aligned[:, 0] + aligned[:, 1]
        diff = aligned[:, 0] - aligned[:, 1]
        c_idx = [int(np.argmin(s)), int(np.argmax(diff)), int(np.argmax(s)), int(np.argmin(diff))]

        if len(set(c_idx)) == 4:
            quad_rot = pts[c_idx]
            is_valid, _ = validate_quadrilateral(quad_rot)
            if is_valid and cv2.isContourConvex(quad_rot.astype(np.int32)):
                return quad_rot
    except Exception:
        pass

    # Method 2: Standard Extrema (TL, TR, BR, BL)
    try:
        s = pts[:, 0] + pts[:, 1]
        diff = pts[:, 0] - pts[:, 1]
        c_idx = [int(np.argmin(s)), int(np.argmax(diff)), int(np.argmax(s)), int(np.argmin(diff))]
        if len(set(c_idx)) == 4:
            quad_ext = pts[c_idx]
            is_valid, _ = validate_quadrilateral(quad_ext)
            if is_valid and cv2.isContourConvex(quad_ext.astype(np.int32)):
                return quad_ext
    except Exception:
        pass

    # Method 3: Combinatorial area maximization for simplified polygon
    search_pts = pts
    if N > 10:
        peri = cv2.arcLength(pts.reshape(-1, 1, 2).astype(np.int32), True)
        approx = cv2.approxPolyDP(pts.reshape(-1, 1, 2).astype(np.int32), 0.02 * peri, True)
        search_pts = approx.reshape(-1, 2).astype(np.float32)
        if len(search_pts) < 4:
            return None
        if len(search_pts) == 4:
            is_valid, _ = validate_quadrilateral(search_pts)
            return search_pts if is_valid else None
        if len(search_pts) > 10:
            search_pts = search_pts[:10]

    best_quad = None
    max_area = 0.0
    for quad_tuple in combinations(search_pts, 4):
        quad_arr = np.array(quad_tuple, dtype=np.float32)
        is_valid, _ = validate_quadrilateral(quad_arr)
        if is_valid and cv2.isContourConvex(quad_arr.astype(np.int32)):
            a = cv2.contourArea(quad_arr)
            if a > max_area:
                max_area = a
                best_quad = quad_arr

    return best_quad

def refine_corners_subpixel(corners: np.ndarray, gray_img: np.ndarray) -> np.ndarray:
    """
    Refines corner coordinates to sub-pixel accuracy using gradient zero-crossing.
    """
    try:
        corners_copy = corners.copy().astype(np.float32)
        criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 20, 0.01)
        refined = cv2.cornerSubPix(gray_img, corners_copy, (5, 5), (-1, -1), criteria)
        is_valid, _ = validate_quadrilateral(refined)
        if is_valid:
            return refined
    except Exception:
        pass
    return corners

def score_document_candidate(
    quad: np.ndarray,
    gray_img: np.ndarray,
    total_area: float,
    edge_map: Optional[np.ndarray] = None,
    lap_img: Optional[np.ndarray] = None
) -> float:
    """
    Computes an intelligent composite score for a candidate document quadrilateral.
    Evaluates real physical document signatures:
      1. Paper Brightness: Documents are white/light paper (> 130). Severely penalizes dark tables and mousepads.
      2. Text / Content Entropy: Documents contain text characters and printed lines (Laplacian std dev).
      3. Background Contrast: The document paper is brighter than the supporting desk/surface.
      4. Physical Edge Alignment: Polygon perimeter aligns with actual gradient ridges in the image.
      5. Geometry: Perspective edge parallelism, convexity, and plausible aspect ratio.
      6. Area Plausibility: 15% to 88% of frame is ideal; camera frames (> 95%) are disqualified.
    """
    quad_area = cv2.contourArea(quad)
    area_ratio = quad_area / total_area

    # Area Score
    if area_ratio > 0.95 or area_ratio < 0.06:
        # Camera viewport frame or tiny noise
        return 0.01
    elif 0.15 <= area_ratio <= 0.88:
        # Ideal document area
        area_score = 0.6 + 0.4 * min(1.0, area_ratio / 0.80)
    else:
        area_score = (area_ratio / 0.15) * 0.5

    # Order corners for geometry checks
    ordered = order_corners(quad)
    w1 = np.linalg.norm(ordered[1] - ordered[0])
    w2 = np.linalg.norm(ordered[2] - ordered[3])
    h1 = np.linalg.norm(ordered[3] - ordered[0])
    h2 = np.linalg.norm(ordered[2] - ordered[1])

    if min(w1, w2) < 20 or min(h1, h2) < 20:
        return 0.0

    rw = min(w1, w2) / max(w1, w2)
    rh = min(h1, h2) / max(h1, h2)
    parallel_score = (rw + rh) / 2.0

    # Aspect Ratio Score
    avg_w = (w1 + w2) / 2.0
    avg_h = (h1 + h2) / 2.0
    aspect = avg_w / (avg_h + 1e-5)
    if 0.35 <= aspect <= 3.2:
        aspect_score = 1.0
    elif 0.22 <= aspect <= 4.5:
        aspect_score = 0.5
    else:
        aspect_score = 0.1

    # Regional Masking
    mask_in = np.zeros_like(gray_img)
    cv2.fillPoly(mask_in, [ordered.astype(np.int32)], 255)
    mean_inside = cv2.mean(gray_img, mask=mask_in)[0]

    mask_out = cv2.bitwise_not(mask_in)
    mean_outside = cv2.mean(gray_img, mask=mask_out)[0]

    # 1. Paper Brightness: Documents are white or light paper
    # Strongly penalizes dark desks, dark tables, and mousepads (mean < 110)
    brightness_score = np.clip((mean_inside - 100.0) / 130.0, 0.0, 1.0)
    if mean_inside < 95.0:
        # Strongly penalize dark objects being falsely identified as white paper
        brightness_score *= 0.15

    # 2. Text / Content Density: Real documents contain text and lines
    text_score = 0.5
    if lap_img is not None:
        std_lap = cv2.meanStdDev(lap_img, mask=mask_in)[1][0][0]
        text_score = min(1.0, std_lap / 22.0)

    # 3. Paper vs Background Contrast: Document is brighter than the desk
    contrast_diff = mean_inside - mean_outside
    contrast_score = np.clip((contrast_diff + 20.0) / 90.0, 0.0, 1.0)

    # 4. Edge Alignment: Polygon perimeter must align with real gradient peaks
    edge_score = 0.5
    if edge_map is not None:
        mask_edge = np.zeros_like(edge_map)
        cv2.polylines(mask_edge, [ordered.astype(np.int32)], isClosed=True, color=255, thickness=3)
        edge_pixels = max(1, cv2.countNonZero(mask_edge))
        overlap = cv2.countNonZero(cv2.bitwise_and(mask_edge, edge_map))
        edge_score = min(1.0, (overlap / edge_pixels) * 5.0)

    # Composite weighted score prioritizing document characteristics over empty tables
    composite = (
        (brightness_score * 0.25) +
        (text_score * 0.25) +
        (contrast_score * 0.20) +
        (edge_score * 0.15) +
        (parallel_score * 0.10) +
        (aspect_score * 0.05)
    )

    if area_ratio > 0.94:
        composite *= 0.05

    return float(composite)

def extract_candidates_from_binary_map(
    binary_map: np.ndarray,
    gray_img: np.ndarray,
    min_area: float,
    max_area: float,
    total_area: float,
    strategy_name: str,
    edge_map: Optional[np.ndarray] = None,
    lap_img: Optional[np.ndarray] = None
) -> List[Dict[str, Any]]:
    """
    Extracts and scores candidate document quadrilaterals from a binary map
    using both external and nested contour hierarchies.
    """
    candidates = []
    epsilon_ratios = [0.015, 0.02, 0.025, 0.03, 0.04, 0.06, 0.08]

    # Test both external contours and nested contours (RETR_LIST)
    for ret_mode in [cv2.RETR_EXTERNAL, cv2.RETR_LIST]:
        contours, _ = cv2.findContours(binary_map, ret_mode, cv2.CHAIN_APPROX_SIMPLE)
        if not contours:
            continue

        sorted_cnts = sorted(contours, key=cv2.contourArea, reverse=True)

        for c in sorted_cnts[:16]:
            c_area = cv2.contourArea(c)
            if c_area < min_area or c_area > max_area:
                continue

            peri = cv2.arcLength(c, True)
            if peri <= 0:
                continue

            quad_found = None
            quad_type = "approx"

            # 1. Multi-epsilon Douglas-Peucker search
            for eps in epsilon_ratios:
                approx = cv2.approxPolyDP(c, eps * peri, True)
                if len(approx) == 4:
                    pts = approx.reshape(4, 2).astype(np.float32)
                    is_valid, _ = validate_quadrilateral(pts)
                    if is_valid and cv2.isContourConvex(approx):
                        quad_found = pts
                        quad_type = f"{strategy_name}_approx"
                        break

            # 2. Convex Hull approximation & Rotated Extrema extraction
            if quad_found is None:
                hull = cv2.convexHull(c)
                hull_peri = cv2.arcLength(hull, True)
                if hull_peri > 0:
                    for eps in epsilon_ratios:
                        approx_hull = cv2.approxPolyDP(hull, eps * hull_peri, True)
                        if len(approx_hull) == 4:
                            pts = approx_hull.reshape(4, 2).astype(np.float32)
                            is_valid, _ = validate_quadrilateral(pts)
                            if is_valid and cv2.isContourConvex(approx_hull):
                                quad_found = pts
                                quad_type = f"{strategy_name}_hull"
                                break

                    # If hull has >= 4 vertices, extract 4 corners via rotated extrema
                    if quad_found is None and len(hull) >= 4:
                        quad_best = extract_4_corners_from_polygon(hull)
                        if quad_best is not None:
                            quad_found = quad_best
                            quad_type = f"{strategy_name}_best_hull_area"

            # 3. MinAreaRect Bounding Box fallback
            if quad_found is None and c_area > (total_area * 0.12):
                rect = cv2.minAreaRect(c)
                box = cv2.boxPoints(rect).astype(np.float32)
                box_area = cv2.contourArea(box)
                if box_area > 0 and (c_area / box_area) >= 0.72:
                    is_valid, _ = validate_quadrilateral(box)
                    if is_valid:
                        quad_found = box
                        quad_type = f"{strategy_name}_min_area_rect"

            if quad_found is not None:
                score = score_document_candidate(
                    quad_found, gray_img, total_area, edge_map=edge_map, lap_img=lap_img
                )
                candidates.append({
                    "points": quad_found,
                    "score": score,
                    "method": quad_type,
                    "area": float(cv2.contourArea(quad_found)),
                    "perimeter": peri
                })

    return candidates

def detect_document(
    image_rgb: np.ndarray,
    target_dim: Optional[int] = None
) -> Tuple[bool, Optional[np.ndarray], str, Optional[float], Optional[float], Dict[str, Any]]:
    """
    Robust State-of-the-Art Document Detection Pipeline:
    1. Downsamples image preserving aspect ratio for stable gradient computation.
    2. Erases internal text via morphological closing (17x17), producing solid paper sheets.
    3. Generates multi-modal solid region binary maps:
       - HSV Chroma/Luminance Paper Mask (low saturation, high value)
       - Morphologically Closed Macro Otsu (Direct & Inverted)
       - Adaptive Gaussian Luminance (Direct & Inverted)
       - Multi-Channel Color Canny Edge Closed Regions
       - Standard & CLAHE Luminance Canny
    4. Evaluates contours across external and nested hierarchies (RETR_LIST).
    5. Evaluates candidate quadrilaterals with rotated extrema & sub-pixel refinement.
    6. Ranks candidates using physical paper signatures (brightness, text variance, contrast, edge alignment).
    7. Selects the true document boundary and scales coordinates back.
    """
    orig_h, orig_w = image_rgb.shape[:2]
    total_area_orig = float(orig_w * orig_h)

    # 1. Resize for fast and stable edge detection
    resized_img, sx, sy = resize_for_detection(image_rgb, target_dim or settings.detection_target_dim)
    res_h, res_w = resized_img.shape[:2]
    total_area_res = float(res_w * res_h)
    min_area_res = total_area_res * 0.06
    max_area_res = total_area_res * 0.94

    gray_res = cv2.cvtColor(resized_img, cv2.COLOR_RGB2GRAY)
    lap_res = cv2.Laplacian(gray_res, cv2.CV_64F)

    diagnostics = {
        "resized_width": res_w,
        "resized_height": res_h,
        "scale_x": sx,
        "scale_y": sy,
    }

    all_candidates: List[Dict[str, Any]] = []

    # Morphological kernels
    k17 = cv2.getStructuringElement(cv2.MORPH_RECT, (17, 17))
    k9 = cv2.getStructuringElement(cv2.MORPH_RECT, (9, 9))

    # Precompute Multi-Channel Color Canny Edge Map (Primary edge reference)
    edges_r = cv2.Canny(cv2.GaussianBlur(resized_img[:, :, 0], (5, 5), 0), 30, 100)
    edges_g = cv2.Canny(cv2.GaussianBlur(resized_img[:, :, 1], (5, 5), 0), 30, 100)
    edges_b = cv2.Canny(cv2.GaussianBlur(resized_img[:, :, 2], (5, 5), 0), 30, 100)
    edges_color = np.maximum(edges_r, np.maximum(edges_g, edges_b))
    edges_color_closed = cv2.morphologyEx(edges_color, cv2.MORPH_CLOSE, k9, iterations=1)

    # Text-Erased Closed Grayscale (Removes all text characters while keeping boundary sharp)
    closed_gray = cv2.morphologyEx(gray_res, cv2.MORPH_CLOSE, k17)

    # Modality 1: HSV Color-Space Paper Mask (Extremely robust for colored tables/desks)
    hsv = cv2.cvtColor(resized_img, cv2.COLOR_RGB2HSV)
    th_hsv = ((hsv[:, :, 1] < 85) & (hsv[:, :, 2] > 95)).astype(np.uint8) * 255
    th_hsv = cv2.morphologyEx(th_hsv, cv2.MORPH_CLOSE, k17)
    all_candidates.extend(
        extract_candidates_from_binary_map(
            th_hsv, gray_res, min_area_res, max_area_res, total_area_res, "hsv_paper",
            edge_map=edges_color, lap_img=lap_res
        )
    )

    # Modality 2: Text-Erased Macro Otsu Binarization (Direct & Inverted)
    _, thresh_otsu = cv2.threshold(closed_gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    thresh_otsu_closed = cv2.morphologyEx(thresh_otsu, cv2.MORPH_CLOSE, k9, iterations=2)
    all_candidates.extend(
        extract_candidates_from_binary_map(
            thresh_otsu_closed, gray_res, min_area_res, max_area_res, total_area_res, "otsu_macro",
            edge_map=edges_color, lap_img=lap_res
        )
    )
    thresh_otsu_inv = cv2.bitwise_not(thresh_otsu_closed)
    all_candidates.extend(
        extract_candidates_from_binary_map(
            thresh_otsu_inv, gray_res, min_area_res, max_area_res, total_area_res, "otsu_macro_inv",
            edge_map=edges_color, lap_img=lap_res
        )
    )

    # Modality 3: Text-Erased Adaptive Gaussian Binarization (Handles non-uniform cast shadows)
    thresh_adapt = cv2.adaptiveThreshold(
        closed_gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 51, 8
    )
    thresh_adapt_closed = cv2.morphologyEx(thresh_adapt, cv2.MORPH_CLOSE, k9, iterations=2)
    all_candidates.extend(
        extract_candidates_from_binary_map(
            thresh_adapt_closed, gray_res, min_area_res, max_area_res, total_area_res, "adaptive_macro",
            edge_map=edges_color, lap_img=lap_res
        )
    )
    thresh_adapt_inv = cv2.bitwise_not(thresh_adapt_closed)
    all_candidates.extend(
        extract_candidates_from_binary_map(
            thresh_adapt_inv, gray_res, min_area_res, max_area_res, total_area_res, "adaptive_macro_inv",
            edge_map=edges_color, lap_img=lap_res
        )
    )

    # Modality 4: Multi-Channel Color Canny Edge Detection
    all_candidates.extend(
        extract_candidates_from_binary_map(
            edges_color_closed, gray_res, min_area_res, max_area_res, total_area_res, "color_canny",
            edge_map=edges_color, lap_img=lap_res
        )
    )

    # Modality 5: Standard Luminance Auto-Canny
    edges_std, _ = preprocess_image(resized_img, method="standard")
    all_candidates.extend(
        extract_candidates_from_binary_map(
            edges_std, gray_res, min_area_res, max_area_res, total_area_res, "standard_canny",
            edge_map=edges_color, lap_img=lap_res
        )
    )

    # Modality 6: CLAHE Enhanced Canny
    edges_clahe, _ = preprocess_image(resized_img, method="clahe_canny")
    all_candidates.extend(
        extract_candidates_from_binary_map(
            edges_clahe, gray_res, min_area_res, max_area_res, total_area_res, "clahe_canny",
            edge_map=edges_color, lap_img=lap_res
        )
    )

    if not all_candidates:
        return False, None, "none", None, None, diagnostics

    # Sort all discovered candidates by their intelligent document score
    all_candidates.sort(key=lambda x: x["score"], reverse=True)
    best_candidate = all_candidates[0]

    pts_res = best_candidate["points"].copy()

    # Optional sub-pixel corner refinement
    pts_res = refine_corners_subpixel(pts_res, gray_res)

    # Clamp to resized dimensions
    pts_res[:, 0] = np.clip(pts_res[:, 0], 0, res_w - 1)
    pts_res[:, 1] = np.clip(pts_res[:, 1], 0, res_h - 1)

    # Scale back to full original image coordinates
    pts_orig = np.zeros_like(pts_res)
    pts_orig[:, 0] = np.clip(pts_res[:, 0] / sx, 0, orig_w - 1)
    pts_orig[:, 1] = np.clip(pts_res[:, 1] / sy, 0, orig_h - 1)

    is_valid, _ = validate_quadrilateral(pts_orig)
    if is_valid:
        ordered_pts = order_corners(pts_orig)
        orig_area = float(cv2.contourArea(ordered_pts))
        peri = float(cv2.arcLength(ordered_pts.reshape(-1, 1, 2).astype(np.int32), True))
        return True, ordered_pts, best_candidate["method"], orig_area, peri, diagnostics

    return False, None, "none", None, None, diagnostics

def draw_document_annotation(
    image_rgb: np.ndarray,
    ordered_corners: np.ndarray,
    line_color: Tuple[int, int, int] = (16, 185, 129),  # Emerald Green in RGB
    point_color: Tuple[int, int, int] = (239, 68, 68),  # Red in RGB
    radius: int = 8,
    thickness: int = 3
) -> np.ndarray:
    """
    Draws the detected quadrilateral, edges, and labeled corner circles on a copy of the image.
    ordered_corners: [TL, TR, BR, BL]
    """
    annotated = image_rgb.copy()
    pts_int = np.int32(np.round(ordered_corners)).reshape((-1, 1, 2))

    diag = np.sqrt(annotated.shape[0]**2 + annotated.shape[1]**2)
    dyn_thickness = max(2, int(round(diag / 400.0)))
    dyn_radius = max(6, int(round(diag / 150.0)))

    # Draw semi-transparent filled polygon overlay
    overlay = annotated.copy()
    cv2.fillPoly(overlay, [pts_int], (16, 185, 129))
    cv2.addWeighted(overlay, 0.25, annotated, 0.75, 0, annotated)

    # Draw boundary polygon edges
    cv2.polylines(annotated, [pts_int], isClosed=True, color=line_color, thickness=dyn_thickness)

    # Draw corners and labels
    labels = ["TL", "TR", "BR", "BL"]
    label_colors = [
        (37, 99, 235),   # Blue for TL
        (147, 51, 234),  # Purple for TR
        (234, 88, 12),   # Orange for BR
        (13, 148, 136)   # Teal for BL
    ]

    for i, (pt, label, col) in enumerate(zip(ordered_corners, labels, label_colors)):
        cx, cy = int(round(pt[0])), int(round(pt[1]))
        cv2.circle(annotated, (cx, cy), dyn_radius + 3, (255, 255, 255), -1)
        cv2.circle(annotated, (cx, cy), dyn_radius, col, -1)
        font_scale = max(0.5, diag / 1200.0)
        offset_x = 12 if "R" in label else -32
        offset_y = -10 if "T" in label else 26
        cv2.putText(
            annotated,
            label,
            (cx + offset_x, cy + offset_y),
            cv2.FONT_HERSHEY_SIMPLEX,
            font_scale,
            (255, 255, 255),
            dyn_thickness + 2,
            cv2.LINE_AA
        )
        cv2.putText(
            annotated,
            label,
            (cx + offset_x, cy + offset_y),
            cv2.FONT_HERSHEY_SIMPLEX,
            font_scale,
            col,
            dyn_thickness,
            cv2.LINE_AA
        )

    return annotated
