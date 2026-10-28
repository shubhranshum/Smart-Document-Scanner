import pytest
import numpy as np
import cv2
from app.services.document_detection import detect_document, draw_document_annotation

def create_synthetic_document_image(w=800, h=600):
    """
    Creates a synthetic document on a textured background.
    """
    # Background: dark wood/slate tone
    img = np.full((h, w, 3), 45, dtype=np.uint8)

    # Document corners (rotated rectangle)
    doc_pts = np.array([
        [120, 80],
        [680, 110],
        [630, 520],
        [90, 480]
    ], dtype=np.int32)

    # Fill document with bright off-white
    cv2.fillPoly(img, [doc_pts], (240, 240, 242))

    # Add pseudo text lines
    for y_offset in range(150, 450, 25):
        p1 = (140, y_offset)
        p2 = (600, y_offset + 10)
        cv2.line(img, p1, p2, (30, 30, 30), 2)

    return img, doc_pts

def test_detect_synthetic_document():
    img, expected_pts = create_synthetic_document_image()
    detected, corners, method, area, peri, diag = detect_document(img)

    assert detected is True
    assert corners is not None
    assert len(corners) == 4
    assert area is not None and area > 10000

    # Verify detected corners match expected corners within a small margin of error (<= 15 pixels)
    for c in corners:
        # Distance to closest expected point
        dists = np.linalg.norm(expected_pts - c, axis=1)
        assert np.min(dists) < 15.0

def test_detect_blank_image_fails_gracefully():
    # Pure blank image with no edges/document
    blank_img = np.full((400, 400, 3), 128, dtype=np.uint8)
    detected, corners, method, area, peri, diag = detect_document(blank_img)

    assert detected is False
    assert corners is None

def test_draw_document_annotation():
    img = np.zeros((300, 300, 3), dtype=np.uint8)
    corners = np.array([
        [50, 50],
        [250, 50],
        [250, 250],
        [50, 250]
    ], dtype=np.float32)

    annotated = draw_document_annotation(img, corners)
    assert annotated.shape == img.shape
    # Check that pixels were drawn on annotated
    assert np.any(annotated > 0)
