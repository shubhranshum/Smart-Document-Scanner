from typing import List, Tuple, Dict, Any
import numpy as np

def compute_corner_errors(
    detected_corners: np.ndarray,
    ground_truth_corners: np.ndarray,
    image_shape: Tuple[int, int]
) -> Dict[str, float]:
    """
    Computes Euclidean corner errors between detected and ground truth corners.
    Both should be shape (4, 2) and ordered consistently [TL, TR, BR, BL].
    Returns:
      - corner_errors: list of 4 Euclidean distances in pixels
      - mean_error: average pixel error across 4 corners
      - max_error: maximum corner error in pixels
      - normalized_mean_error: mean_error divided by image diagonal (resolution invariant)
      - image_diagonal: diagonal in pixels
    """
    detected = np.asarray(detected_corners, dtype=np.float32).reshape((4, 2))
    gt = np.asarray(ground_truth_corners, dtype=np.float32).reshape((4, 2))

    # Euclidean distance per corner
    distances = np.linalg.norm(detected - gt, axis=1)
    mean_err = float(np.mean(distances))
    max_err = float(np.max(distances))

    h, w = image_shape[:2]
    diagonal = float(np.sqrt(w**2 + h**2))
    norm_mean_err = mean_err / diagonal if diagonal > 0 else 0.0

    return {
        "tl_error": float(distances[0]),
        "tr_error": float(distances[1]),
        "br_error": float(distances[2]),
        "bl_error": float(distances[3]),
        "mean_error": mean_err,
        "max_error": max_err,
        "normalized_mean_error": norm_mean_err,
        "image_diagonal": diagonal
    }
