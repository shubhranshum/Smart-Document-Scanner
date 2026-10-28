from typing import Tuple, Dict, Optional
import cv2
import numpy as np
from app.config import settings

def resize_for_detection(image: np.ndarray, target_dim: int = None) -> Tuple[np.ndarray, float, float]:
    """
    Resizes image preserving aspect ratio so the max dimension is target_dim.
    Returns: (resized_image, scale_x, scale_y)
    scale_x = w_resized / w_original
    scale_y = h_resized / h_original
    """
    if target_dim is None:
        target_dim = settings.detection_target_dim

    h, w = image.shape[:2]
    max_dim = max(h, w)

    if max_dim <= target_dim:
        return image.copy(), 1.0, 1.0

    scale = target_dim / float(max_dim)
    new_w = max(1, int(round(w * scale)))
    new_h = max(1, int(round(h * scale)))

    resized = cv2.resize(image, (new_w, new_h), interpolation=cv2.INTER_AREA)
    scale_x = new_w / float(w)
    scale_y = new_h / float(h)

    return resized, scale_x, scale_y

def compute_auto_canny_thresholds(gray: np.ndarray, sigma: float = 0.33) -> Tuple[int, int]:
    """
    Computes optimal Canny thresholds based on median pixel intensity.
    """
    v = np.median(gray)
    lower = int(max(10, (1.0 - sigma) * v))
    upper = int(min(245, (1.0 + sigma) * v))
    if lower >= upper:
        lower = max(10, int(v * 0.5))
        upper = min(245, int(v * 1.5))
    return lower, upper

def preprocess_image(
    image_rgb: np.ndarray,
    method: str = "standard",
    canny_thresh: Optional[Tuple[int, int]] = None
) -> Tuple[np.ndarray, Dict[str, np.ndarray]]:
    """
    Preprocesses an image for contour/edge detection using multi-modal strategies:
      - 'standard': Gaussian blur + Auto-Canny + (5x5) morphological closing
      - 'clahe_canny': CLAHE luminance enhancement + Canny + (7x7) closing
      - 'color_canny': Multi-channel RGB Canny union + (5x5) closing
      - 'adaptive': Bilateral filter + Adaptive Gaussian Thresholding + (7x7) closing
      - 'otsu': Gaussian blur + Otsu binarization + (7x7) closing
      - 'morph_gradient': Morphological gradient operator + Canny
    Returns: (binary_edge_map, intermediate_diagnostics)
    """
    diagnostics = {}

    # Extract single-channel grayscale
    if len(image_rgb.shape) == 3:
        gray = cv2.cvtColor(image_rgb, cv2.COLOR_RGB2GRAY)
    else:
        gray = image_rgb.copy()
    diagnostics["grayscale"] = gray

    # Kernel definitions for closing
    k3 = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
    k5 = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
    k7 = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7))

    if method == "standard":
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        diagnostics["blurred"] = blurred

        if canny_thresh is None:
            lower, upper = compute_auto_canny_thresholds(blurred)
        else:
            lower, upper = canny_thresh

        edges = cv2.Canny(blurred, lower, upper)
        # Seal small gaps along document perimeter
        closed = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, k5, iterations=1)
        closed = cv2.dilate(closed, k3, iterations=1)
        diagnostics["edges_closed"] = closed
        return closed, diagnostics

    elif method == "clahe_canny":
        # Boost local contrast in shadowed/faint border areas
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
        enhanced_gray = clahe.apply(gray)
        blurred = cv2.bilateralFilter(enhanced_gray, 7, 50, 50)
        diagnostics["clahe_gray"] = enhanced_gray

        if canny_thresh is None:
            lower, upper = compute_auto_canny_thresholds(blurred, sigma=0.4)
        else:
            lower, upper = canny_thresh

        edges = cv2.Canny(blurred, lower, upper)
        closed = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, k7, iterations=1)
        closed = cv2.dilate(closed, k3, iterations=1)
        diagnostics["edges_closed"] = closed
        return closed, diagnostics

    elif method == "color_canny":
        # Compute gradient across individual R, G, B channels
        if len(image_rgb.shape) == 3:
            edges_r = cv2.Canny(cv2.GaussianBlur(image_rgb[:, :, 0], (5, 5), 0), 30, 120)
            edges_g = cv2.Canny(cv2.GaussianBlur(image_rgb[:, :, 1], (5, 5), 0), 30, 120)
            edges_b = cv2.Canny(cv2.GaussianBlur(image_rgb[:, :, 2], (5, 5), 0), 30, 120)
            edges = np.maximum(edges_r, np.maximum(edges_g, edges_b))
        else:
            edges = cv2.Canny(cv2.GaussianBlur(gray, (5, 5), 0), 30, 120)

        closed = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, k5, iterations=1)
        closed = cv2.dilate(closed, k3, iterations=1)
        diagnostics["edges_closed"] = closed
        return closed, diagnostics

    elif method == "adaptive":
        blurred = cv2.bilateralFilter(gray, 9, 75, 75)
        diagnostics["blurred"] = blurred

        thresh = cv2.adaptiveThreshold(
            blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY_INV, 31, 5
        )
        diagnostics["adaptive_thresh"] = thresh

        closed = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, k7, iterations=2)
        diagnostics["edges_closed"] = closed
        return closed, diagnostics

    elif method == "otsu":
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        _, thresh = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        diagnostics["otsu_thresh"] = thresh

        edges = cv2.Canny(thresh, 50, 150)
        closed = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, k5, iterations=1)
        diagnostics["edges_closed"] = closed
        return closed, diagnostics

    else:
        # Fallback to standard
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        edges = cv2.Canny(blurred, 30, 120)
        closed = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, k5, iterations=1)
        return closed, diagnostics
