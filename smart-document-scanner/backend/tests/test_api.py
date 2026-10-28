import io
import json
import numpy as np
import cv2
from PIL import Image
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def create_image_bytes(w=400, h=300, is_doc=True):
    img = np.full((h, w, 3), 40, dtype=np.uint8)
    if is_doc:
        doc_pts = np.array([
            [50, 40],
            [350, 50],
            [340, 260],
            [40, 250]
        ], dtype=np.int32)
        cv2.fillPoly(img, [doc_pts], (240, 240, 240))
        for y in range(70, 230, 20):
            cv2.line(img, (60, y), (330, y), (20, 20, 20), 2)
    pil = Image.fromarray(img)
    buf = io.BytesIO()
    pil.save(buf, format="PNG")
    return buf.getvalue()

def test_health_endpoint():
    res = client.get("/api/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "healthy"
    assert "opencv_version" in data
    assert "backend_version" in data

def test_detect_endpoint_success():
    img_bytes = create_image_bytes(is_doc=True)
    res = client.post(
        "/api/detect",
        files={"file": ("document.png", img_bytes, "image/png")},
        data={"include_diagnostics": "true"}
    )
    assert res.status_code == 200
    data = res.json()
    assert data["detected"] is True
    assert len(data["corners"]) == 4
    assert data["preview_image"].startswith("data:image/png;base64,")

def test_detect_endpoint_no_document():
    img_bytes = create_image_bytes(is_doc=False)
    res = client.post(
        "/api/detect",
        files={"file": ("blank.png", img_bytes, "image/png")}
    )
    assert res.status_code == 200
    data = res.json()
    # Detection failure is graceful, not 500
    assert data["detected"] is False

def test_correct_endpoint():
    img_bytes = create_image_bytes(is_doc=True)
    corners = json.dumps([
        {"x": 50, "y": 40},
        {"x": 350, "y": 50},
        {"x": 340, "y": 260},
        {"x": 40, "y": 250}
    ])
    res = client.post(
        "/api/correct",
        files={"file": ("document.png", img_bytes, "image/png")},
        data={"corners": corners}
    )
    assert res.status_code == 200
    data = res.json()
    assert "corrected_image" in data
    assert data["output_width"] > 0
    assert data["output_height"] > 0

def test_enhance_endpoint_modes():
    img_bytes = create_image_bytes(is_doc=True)
    modes = ["color", "grayscale", "black_white", "contrast"]
    for mode in modes:
        res = client.post(
            "/api/enhance",
            files={"file": ("document.png", img_bytes, "image/png")},
            data={"mode": mode}
        )
        assert res.status_code == 200
        data = res.json()
        assert data["mode"] == mode
        assert data["enhanced_image"].startswith("data:image/png;base64,")

def test_process_endpoint_end_to_end():
    img_bytes = create_image_bytes(is_doc=True)
    res = client.post(
        "/api/process",
        files={"file": ("document.png", img_bytes, "image/png")},
        data={"enhancement_mode": "black_white"}
    )
    assert res.status_code == 200
    data = res.json()
    assert data["detected"] is True
    assert data["corrected_image"] is not None
    assert data["enhanced_image"] is not None

def test_export_pdf_endpoint():
    img_bytes = create_image_bytes(is_doc=True)
    res = client.post(
        "/api/export/pdf",
        files={"file": ("document.png", img_bytes, "image/png")},
        data={"title": "Test Doc"}
    )
    assert res.status_code == 200
    assert res.headers["content-type"] == "application/pdf"
    assert res.content.startswith(b"%PDF")
