import pytest
import numpy as np
from app.services.perspective import (
    validate_quadrilateral,
    order_corners,
    compute_perspective_transform_dimensions,
    apply_perspective_correction
)

def test_validate_quadrilateral_valid():
    # Regular rectangle
    pts = np.array([
        [50, 50],
        [300, 60],
        [290, 400],
        [40, 390]
    ], dtype=np.float32)
    is_valid, err = validate_quadrilateral(pts)
    assert is_valid is True
    assert err is None

def test_validate_quadrilateral_self_intersecting():
    # Bow-tie / hourglass shape
    pts = np.array([
        [50, 50],
        [300, 400],
        [300, 50],
        [50, 400]
    ], dtype=np.float32)
    is_valid, err = validate_quadrilateral(pts)
    assert is_valid is False
    assert "non-convex" in err or "self-intersecting" in err

def test_validate_quadrilateral_collinear():
    # Degenerate collinear points
    pts = np.array([
        [50, 50],
        [100, 50],
        [200, 50],
        [300, 50]
    ], dtype=np.float32)
    is_valid, err = validate_quadrilateral(pts)
    assert is_valid is False

def test_order_corners_ordering():
    # Shuffle the corners of a rectangle
    # Clockwise should be TL: (10, 10), TR: (200, 15), BR: (195, 300), BL: (15, 290)
    pts = np.array([
        [195, 300],  # BR
        [10, 10],    # TL
        [15, 290],   # BL
        [200, 15],   # TR
    ], dtype=np.float32)

    ordered = order_corners(pts)
    assert len(ordered) == 4

    tl, tr, br, bl = ordered
    assert np.allclose(tl, [10, 10])
    assert np.allclose(tr, [200, 15])
    assert np.allclose(br, [195, 300])
    assert np.allclose(bl, [15, 290])

def test_perspective_correction_output():
    # Create test image with distinct quadrant colors
    img = np.zeros((400, 500, 3), dtype=np.uint8)
    img[50:350, 50:450] = 255  # white document inside black border

    corners = np.array([
        [50, 50],
        [450, 50],
        [450, 350],
        [50, 350]
    ], dtype=np.float32)

    warped, out_w, out_h, M = apply_perspective_correction(img, corners)
    assert out_w > 0
    assert out_h > 0
    assert warped.shape == (out_h, out_w, 3)
    # The warped output should be mostly white
    assert np.mean(warped) > 240
