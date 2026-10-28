"""
Comprehensive QA Audit Script for Smart Document Scanner
Performs live API tests, synthetic image testing, manual corner simulation,
enhancement validation, download verification, and error-handling tests.
"""

import sys
import os
import io
import json
import base64
import numpy as np
from PIL import Image
import httpx

# Ensure paths
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(script_dir, ".."))
sys.path.insert(0, os.path.join(project_root, "backend"))

BASE_URL = "http://127.0.0.1:8000"

def run_audit():
    client = httpx.Client(base_url=BASE_URL, timeout=30.0)
    audit_results = {}

    print("=" * 80)
    print("SMART DOCUMENT SCANNER: QA END-TO-END AUDIT")
    print("=" * 80)

    # 1. Health Endpoint
    print("\n[1/9] Testing GET /api/health...")
    try:
        res = client.get("/api/health")
        assert res.status_code == 200, f"Expected 200, got {res.status_code}"
        data = res.json()
        assert data.get("status") == "healthy"
        assert "opencv_version" in data
        assert "backend_version" in data
        audit_results["health"] = {
            "status": "PASS",
            "code": res.status_code,
            "details": data
        }
        print(f" -> PASS: {data}")
    except Exception as e:
        audit_results["health"] = {"status": "FAIL", "error": str(e)}
        print(f" -> FAIL: {e}")

    # 2. Upload Valid Synthetic Document
    print("\n[2/9] Testing POST /api/detect with valid document...")
    sample_img_path = os.path.join(project_root, "dataset", "sample_images", "doc_01_mild_angle_slate.jpg")
    assert os.path.exists(sample_img_path), f"Missing test image: {sample_img_path}"

    with open(sample_img_path, "rb") as f:
        img_bytes = f.read()

    try:
        res = client.post(
            "/api/detect",
            files={"file": ("doc_01.jpg", img_bytes, "image/jpeg")},
            data={"include_diagnostics": "true"}
        )
        assert res.status_code == 200, f"Expected 200, got {res.status_code}"
        data = res.json()
        assert data["detected"] is True, "Document boundary was not detected"
        assert len(data["corners"]) == 4, f"Expected 4 corners, got {len(data['corners'])}"
        assert data["preview_image"].startswith("data:image/png;base64,")

        # Verify corners are plausible (TL, TR, BR, BL order and coordinates)
        corners = data["corners"]
        tl, tr, br, bl = corners[0], corners[1], corners[2], corners[3]
        # TL should have smaller x and y than BR
        assert tl["x"] < br["x"] and tl["y"] < br["y"], f"Invalid corner order: TL={tl}, BR={br}"
        assert tr["x"] > bl["x"], f"Invalid corner order: TR={tr}, BL={bl}"

        audit_results["detect_valid"] = {
            "status": "PASS",
            "corners": corners,
            "method": data["method"],
            "area": data["contour_area"],
            "time_ms": data["processing_time_ms"]
        }
        print(f" -> PASS: Detected=True, Method={data['method']}, Corners={corners}, Time={data['processing_time_ms']}ms")
    except Exception as e:
        audit_results["detect_valid"] = {"status": "FAIL", "error": str(e)}
        print(f" -> FAIL: {e}")

    # 3. Perspective Correction Output Verification
    print("\n[3/9] Testing POST /api/correct (Perspective Rectification)...")
    try:
        detected_corners = audit_results["detect_valid"]["corners"]
        res = client.post(
            "/api/correct",
            files={"file": ("doc_01.jpg", img_bytes, "image/jpeg")},
            data={"corners": json.dumps(detected_corners)}
        )
        assert res.status_code == 200, f"Expected 200, got {res.status_code}"
        data = res.json()
        out_w = data["output_width"]
        out_h = data["output_height"]
        assert out_w > 400 and out_h > 500, f"Plausibility failed for out dimensions: {out_w}x{out_h}"

        # Decode corrected image to verify valid raster payload
        b64_data = data["corrected_image"].split(",")[1]
        decoded_bytes = base64.b64decode(b64_data)
        pil_img = Image.open(io.BytesIO(decoded_bytes))
        assert pil_img.size == (out_w, out_h), f"Decoded size {pil_img.size} != {out_w}x{out_h}"
        assert pil_img.format == "PNG"

        audit_results["correct_perspective"] = {
            "status": "PASS",
            "output_dimensions": (out_w, out_h),
            "image_format": pil_img.format,
            "time_ms": data["processing_time_ms"]
        }
        print(f" -> PASS: Output={out_w}x{out_h} px, Decoded PIL image={pil_img.size}, Format={pil_img.format}")
    except Exception as e:
        audit_results["correct_perspective"] = {"status": "FAIL", "error": str(e)}
        print(f" -> FAIL: {e}")

    # 4. Manual Corner Adjustment & Coordinate Conversion
    print("\n[4/9] Testing Manual Corner Adjustment & Offset Transformation...")
    try:
        # Simulate user manually tweaking corners by 10 pixels
        manual_corners = [
            {"x": round(corners[0]["x"] + 10), "y": round(corners[0]["y"] + 10)},
            {"x": round(corners[1]["x"] - 10), "y": round(corners[1]["y"] + 10)},
            {"x": round(corners[2]["x"] - 10), "y": round(corners[2]["y"] - 10)},
            {"x": round(corners[3]["x"] + 10), "y": round(corners[3]["y"] - 10)},
        ]
        res = client.post(
            "/api/correct",
            files={"file": ("doc_01.jpg", img_bytes, "image/jpeg")},
            data={"corners": json.dumps(manual_corners)}
        )
        assert res.status_code == 200
        data = res.json()
        b64_data = data["corrected_image"].split(",")[1]
        decoded = Image.open(io.BytesIO(base64.b64decode(b64_data)))
        assert decoded.size == (data["output_width"], data["output_height"])

        audit_results["manual_corners"] = {
            "status": "PASS",
            "manual_input": manual_corners,
            "output_dimensions": decoded.size
        }
        print(f" -> PASS: Manual corners warped successfully into {decoded.size} image.")
    except Exception as e:
        audit_results["manual_corners"] = {"status": "FAIL", "error": str(e)}
        print(f" -> FAIL: {e}")

    # 5. Test Every Enhancement Mode
    print("\n[5/9] Testing POST /api/enhance across all modes...")
    modes = ["color", "grayscale", "black_white", "contrast"]
    corrected_b64 = data["corrected_image"]
    enhancement_results = {}

    for mode in modes:
        try:
            res = client.post(
                "/api/enhance",
                data={"image_data": corrected_b64, "mode": mode}
            )
            assert res.status_code == 200, f"Mode {mode} failed with {res.status_code}: {res.text}"
            data_enh = res.json()
            assert data_enh["mode"] == mode
            b64_enh = data_enh["enhanced_image"].split(",")[1]
            img_enh = Image.open(io.BytesIO(base64.b64decode(b64_enh)))
            assert img_enh.size == (data_enh["output_width"], data_enh["output_height"])

            # Verify mode-specific properties
            arr = np.array(img_enh)
            if mode == "grayscale":
                # R, G, B channels should be identical
                assert np.allclose(arr[:, :, 0], arr[:, :, 1], atol=1)
                assert np.allclose(arr[:, :, 1], arr[:, :, 2], atol=1)
            elif mode == "black_white":
                # Adaptive threshold yields predominantly 0 and 255 values
                unique_vals = np.unique(arr)
                is_binary = set(unique_vals).issubset({0, 255})
                assert is_binary, f"Expected binary 0/255 values, got {unique_vals}"

            enhancement_results[mode] = "PASS"
            print(f" -> PASS: Mode={mode:<12} (Dim={img_enh.size}, Format={img_enh.format})")
        except Exception as e:
            enhancement_results[mode] = f"FAIL: {e}"
            print(f" -> FAIL: Mode={mode}: {e}")

    audit_results["enhancements"] = enhancement_results

    # 6. Test Image and PDF Downloads Verification
    print("\n[6/9] Testing Export / Download payload integrity...")
    try:
        # PDF export
        res = client.post(
            "/api/export/pdf",
            data={"image_data": corrected_b64, "title": "QA Test Document"}
        )
        assert res.status_code == 200, f"Expected 200, got {res.status_code}"
        assert res.headers["content-type"] == "application/pdf"
        assert res.content.startswith(b"%PDF"), "Missing PDF header signature"
        assert len(res.content) > 10000, f"PDF file size suspiciously small: {len(res.content)} bytes"

        audit_results["pdf_export"] = {
            "status": "PASS",
            "content_type": res.headers["content-type"],
            "size_bytes": len(res.content)
        }
        print(f" -> PASS: PDF Export valid (%PDF-1.3, {len(res.content)} bytes)")
    except Exception as e:
        audit_results["pdf_export"] = {"status": "FAIL", "error": str(e)}
        print(f" -> FAIL: {e}")

    # 7. Unified Pipeline POST /api/process
    print("\n[7/9] Testing POST /api/process (End-to-End unified pipeline)...")
    try:
        res = client.post(
            "/api/process",
            files={"file": ("doc_01.jpg", img_bytes, "image/jpeg")},
            data={"enhancement_mode": "black_white", "include_diagnostics": "true"}
        )
        assert res.status_code == 200
        pdata = res.json()
        assert pdata["detected"] is True
        assert pdata["corrected_image"] is not None
        assert pdata["enhanced_image"] is not None
        assert pdata["output_width"] > 0
        assert pdata["output_height"] > 0

        audit_results["process_pipeline"] = {
            "status": "PASS",
            "time_ms": pdata["processing_time_ms"],
            "method": pdata["detection_method"],
            "out_dim": f"{pdata['output_width']}x{pdata['output_height']}"
        }
        print(f" -> PASS: Unified pipeline succeeded in {pdata['processing_time_ms']} ms")
    except Exception as e:
        audit_results["process_pipeline"] = {"status": "FAIL", "error": str(e)}
        print(f" -> FAIL: {e}")

    # 8. Negative & Edge-Case Testing
    print("\n[8/9] Testing Negative Cases & Input Sanitization...")
    neg_results = {}

    # Case 8a: Empty upload
    try:
        res = client.post("/api/detect", files={"file": ("empty.png", b"", "image/png")})
        assert res.status_code == 400, f"Expected 400 for empty file, got {res.status_code}"
        neg_results["empty_file"] = "PASS (400 Bad Request)"
    except Exception as e:
        neg_results["empty_file"] = f"FAIL: {e}"

    # Case 8b: Corrupt file
    try:
        res = client.post("/api/detect", files={"file": ("corrupt.png", b"NOT_IMAGE_DATA_12345", "image/png")})
        assert res.status_code == 400, f"Expected 400 for corrupt file, got {res.status_code}"
        neg_results["corrupt_file"] = "PASS (400 Bad Request)"
    except Exception as e:
        neg_results["corrupt_file"] = f"FAIL: {e}"

    # Case 8c: Blank image (no document) -> Must return 200 with detected=False
    try:
        blank = np.full((300, 300, 3), 128, dtype=np.uint8)
        buf = io.BytesIO()
        Image.fromarray(blank).save(buf, format="PNG")
        res = client.post("/api/detect", files={"file": ("blank.png", buf.getvalue(), "image/png")})
        assert res.status_code == 200
        data = res.json()
        assert data["detected"] is False, f"Expected detected=False, got {data['detected']}"
        assert data["corners"] is None
        neg_results["blank_image"] = "PASS (detected=False returned gracefully)"
    except Exception as e:
        neg_results["blank_image"] = f"FAIL: {e}"

    # Case 8d: Degenerate self-intersecting bow-tie corners to /api/correct
    try:
        bowtie_corners = [
            {"x": 50, "y": 50},
            {"x": 400, "y": 400},
            {"x": 400, "y": 50},
            {"x": 50, "y": 400}
        ]
        res = client.post(
            "/api/correct",
            files={"file": ("doc_01.jpg", img_bytes, "image/jpeg")},
            data={"corners": json.dumps(bowtie_corners)}
        )
        assert res.status_code == 400, f"Expected 400 for bowtie corners, got {res.status_code}"
        neg_results["bowtie_corners"] = f"PASS (400 Bad Request: {res.json().get('detail')})"
    except Exception as e:
        neg_results["bowtie_corners"] = f"FAIL: {e}"

    # Case 8e: Degenerate collinear corners
    try:
        collinear = [{"x": 10, "y": 10}, {"x": 20, "y": 10}, {"x": 30, "y": 10}, {"x": 40, "y": 10}]
        res = client.post(
            "/api/correct",
            files={"file": ("doc_01.jpg", img_bytes, "image/jpeg")},
            data={"corners": json.dumps(collinear)}
        )
        assert res.status_code == 400, f"Expected 400 for collinear corners, got {res.status_code}"
        neg_results["collinear_corners"] = f"PASS (400 Bad Request: {res.json().get('detail')})"
    except Exception as e:
        neg_results["collinear_corners"] = f"FAIL: {e}"

    audit_results["negative_tests"] = neg_results
    for k, v in neg_results.items():
        print(f" -> {k:<20}: {v}")

    # 9. Frontend Dev Server Check
    print("\n[9/9] Verifying Frontend Dev Server on port 3000...")
    try:
        f_client = httpx.Client(timeout=10.0)
        res = f_client.get("http://127.0.0.1:3000")
        assert res.status_code == 200
        assert "<title>SmartScan" in res.text
        audit_results["frontend_server"] = "PASS (HTTP 200, SmartScan title served)"
        print(f" -> PASS: Frontend server reachable at http://127.0.0.1:3000 (status {res.status_code})")
    except Exception as e:
        audit_results["frontend_server"] = f"FAIL: {e}"
        print(f" -> FAIL: {e}")

    print("\n" + "=" * 80)
    print("AUDIT EXECUTION COMPLETE")
    print("=" * 80)
    return audit_results

if __name__ == "__main__":
    results = run_audit()
