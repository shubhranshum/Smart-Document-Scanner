import time
import json
import logging
from typing import Optional, List
import cv2
import numpy as np
from fastapi import FastAPI, UploadFile, File, Form, HTTPException, status, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response, JSONResponse

from app.config import settings
from app.schemas import (
    Point,
    EnhancementMode,
    HealthResponse,
    DetectionResponse,
    CorrectionResponse,
    EnhanceResponse,
    ProcessResponse,
)
from app.services.image_validation import (
    validate_and_decode_image,
    encode_image_to_base64,
    decode_base64_to_image,
)
from app.services.document_detection import detect_document, draw_document_annotation
from app.services.perspective import apply_perspective_correction, order_corners, validate_quadrilateral
from app.services.enhancement import enhance_image
from app.services.pdf_export import export_image_to_pdf

logger = logging.getLogger("smart_scan")
logging.basicConfig(level=logging.INFO)

app = FastAPI(
    title=settings.app_name,
    version=settings.backend_version,
    description="Intelligent Document Scanner API using OpenCV image processing and perspective transformation.",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def parse_corners_input(corners_raw: Optional[str]) -> Optional[np.ndarray]:
    """
    Parses corners string from JSON input.
    Accepts: [[x1, y1], [x2, y2], [x3, y3], [x4, y4]]
    or [{'x': x1, 'y': y1}, ...]
    """
    if not corners_raw:
        return None
    try:
        data = json.loads(corners_raw)
        if isinstance(data, list) and len(data) == 4:
            if isinstance(data[0], dict) and "x" in data[0] and "y" in data[0]:
                pts = [[float(p["x"]), float(p["y"])] for p in data]
                return np.array(pts, dtype=np.float32)
            elif isinstance(data[0], (list, tuple)) and len(data[0]) >= 2:
                pts = [[float(p[0]), float(p[1])] for p in data]
                return np.array(pts, dtype=np.float32)
        raise ValueError("Corners must be a list of 4 coordinate pairs.")
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Malformed corners data: {str(e)}"
        )

@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception during {request.method} {request.url.path}: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "An internal image processing error occurred. Please check input parameters."}
    )

@app.get("/api/health", response_model=HealthResponse)
def health_check():
    """
    Returns server status, OpenCV version, and backend API version.
    """
    return HealthResponse(
        status="healthy",
        opencv_version=cv2.__version__,
        backend_version=settings.backend_version
    )

@app.post("/api/detect", response_model=DetectionResponse)
async def detect_document_endpoint(
    file: UploadFile = File(...),
    include_diagnostics: bool = Form(False)
):
    """
    Accepts an uploaded photograph, detects document boundaries,
    and returns detected 4 corners and an annotated preview.
    """
    start_time = time.perf_counter()
    file_bytes = await file.read()
    image_rgb, width, height = validate_and_decode_image(file_bytes)
    try:
        cv2.imwrite("dataset/last_uploaded_image.png", cv2.cvtColor(image_rgb, cv2.COLOR_RGB2BGR))
    except Exception:
        pass

    detected, corners, method, area, peri, diag = detect_document(image_rgb)
    elapsed_ms = (time.perf_counter() - start_time) * 1000.0

    preview_b64 = None
    corners_list = None

    if detected and corners is not None:
        corners_list = [Point(x=float(pt[0]), y=float(pt[1])) for pt in corners]
        annotated_img = draw_document_annotation(image_rgb, corners)
        preview_b64 = encode_image_to_base64(annotated_img, format="PNG")
        message = "Document boundary detected successfully."
    else:
        # Provide clean preview even when detection fails
        preview_b64 = encode_image_to_base64(image_rgb, format="PNG")
        message = "Automatic detection could not confidently locate 4 document corners. Please adjust or select corners manually."

    resp_diag = None
    if include_diagnostics:
        resp_diag = {
            "scale_x": diag.get("scale_x"),
            "scale_y": diag.get("scale_y"),
            "resized_width": diag.get("resized_width"),
            "resized_height": diag.get("resized_height"),
        }

    return DetectionResponse(
        detected=detected,
        corners=corners_list,
        method=method if detected else None,
        contour_area=area,
        contour_perimeter=peri,
        image_width=width,
        image_height=height,
        processing_time_ms=round(elapsed_ms, 2),
        preview_image=preview_b64,
        message=message,
        diagnostics=resp_diag
    )

@app.post("/api/correct", response_model=CorrectionResponse)
async def correct_perspective_endpoint(
    file: UploadFile = File(...),
    corners: str = Form(...),
    target_width: Optional[int] = Form(None),
    target_height: Optional[int] = Form(None)
):
    """
    Applies perspective transformation to straighten the document
    defined by four source corner coordinates.
    """
    start_time = time.perf_counter()
    file_bytes = await file.read()
    image_rgb, width, height = validate_and_decode_image(file_bytes)
    try:
        cv2.imwrite("dataset/last_uploaded_image.png", cv2.cvtColor(image_rgb, cv2.COLOR_RGB2BGR))
    except Exception:
        pass

    corner_pts = parse_corners_input(corners)
    if corner_pts is None or len(corner_pts) != 4:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Four corner coordinates are required."
        )

    # Perspective warp
    warped, out_w, out_h, M = apply_perspective_correction(
        image_rgb,
        corner_pts,
        target_width=target_width,
        target_height=target_height
    )

    elapsed_ms = (time.perf_counter() - start_time) * 1000.0
    corrected_b64 = encode_image_to_base64(warped, format="PNG")

    return CorrectionResponse(
        corrected_image=corrected_b64,
        output_width=out_w,
        output_height=out_h,
        processing_time_ms=round(elapsed_ms, 2),
        metadata={
            "homography_matrix": M.tolist(),
            "original_width": width,
            "original_height": height,
        }
    )

@app.post("/api/enhance", response_model=EnhanceResponse)
async def enhance_image_endpoint(
    file: Optional[UploadFile] = File(None),
    image_data: Optional[str] = Form(None),
    mode: EnhancementMode = Form(EnhancementMode.COLOR)
):
    """
    Enhances an image with the selected mode:
    color, grayscale, black_white (adaptive thresholding), contrast (CLAHE).
    """
    start_time = time.perf_counter()

    if file is not None:
        file_bytes = await file.read()
        image_rgb, _, _ = validate_and_decode_image(file_bytes)
    elif image_data is not None:
        image_rgb = decode_base64_to_image(image_data)
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Either an image file or base64 image_data is required."
        )

    enhanced = enhance_image(image_rgb, mode=mode)
    elapsed_ms = (time.perf_counter() - start_time) * 1000.0
    enhanced_b64 = encode_image_to_base64(enhanced, format="PNG")

    return EnhanceResponse(
        enhanced_image=enhanced_b64,
        mode=mode.value,
        output_width=enhanced.shape[1],
        output_height=enhanced.shape[0],
        processing_time_ms=round(elapsed_ms, 2)
    )

@app.post("/api/process", response_model=ProcessResponse)
async def process_document_pipeline(
    file: UploadFile = File(...),
    enhancement_mode: EnhancementMode = Form(EnhancementMode.COLOR),
    corners: Optional[str] = Form(None),
    include_diagnostics: bool = Form(False)
):
    """
    Unified pipeline:
    1. Detects document boundaries (or uses manually provided corners).
    2. Performs perspective transformation.
    3. Applies enhancement.
    If detection fails and no corners are provided, returns detected=false gracefully.
    """
    start_time = time.perf_counter()
    file_bytes = await file.read()
    image_rgb, width, height = validate_and_decode_image(file_bytes)
    try:
        cv2.imwrite("dataset/last_uploaded_image.png", cv2.cvtColor(image_rgb, cv2.COLOR_RGB2BGR))
    except Exception:
        pass

    warnings: List[str] = []
    diag_data = {}

    manual_pts = parse_corners_input(corners)
    if manual_pts is not None:
        detected = True
        corner_pts = manual_pts
        method = "manual_input"
    else:
        detected, corner_pts, method, area, peri, diag = detect_document(image_rgb)
        if include_diagnostics:
            diag_data["scale_x"] = diag.get("scale_x")
            diag_data["scale_y"] = diag.get("scale_y")

    if not detected or corner_pts is None:
        elapsed_ms = (time.perf_counter() - start_time) * 1000.0
        original_preview = encode_image_to_base64(image_rgb, format="PNG")
        return ProcessResponse(
            detected=False,
            annotated_preview=original_preview,
            processing_time_ms=round(elapsed_ms, 2),
            message="Automatic document boundary detection failed. Please use the corner editor to position corners manually.",
            diagnostics=diag_data if include_diagnostics else None
        )

    # Validate corners geometry
    is_valid, err_msg = validate_quadrilateral(corner_pts)
    if not is_valid:
        elapsed_ms = (time.perf_counter() - start_time) * 1000.0
        return ProcessResponse(
            detected=False,
            processing_time_ms=round(elapsed_ms, 2),
            message=f"Corners validation failed: {err_msg}. Please select valid quadrilateral corners."
        )

    # Order corners
    ordered_corners = order_corners(corner_pts)
    corners_list = [Point(x=float(p[0]), y=float(p[1])) for p in ordered_corners]

    # Annotated preview
    annotated = draw_document_annotation(image_rgb, ordered_corners)
    annotated_b64 = encode_image_to_base64(annotated, format="PNG")

    # Perspective Warp
    warped, out_w, out_h, _ = apply_perspective_correction(image_rgb, ordered_corners)
    corrected_b64 = encode_image_to_base64(warped, format="PNG")

    # Enhancement
    enhanced = enhance_image(warped, mode=enhancement_mode)
    enhanced_b64 = encode_image_to_base64(enhanced, format="PNG")

    elapsed_ms = (time.perf_counter() - start_time) * 1000.0

    return ProcessResponse(
        detected=True,
        corners=corners_list,
        annotated_preview=annotated_b64,
        corrected_image=corrected_b64,
        enhanced_image=enhanced_b64,
        output_width=out_w,
        output_height=out_h,
        detection_method=method,
        enhancement_mode=enhancement_mode.value,
        processing_time_ms=round(elapsed_ms, 2),
        warnings=warnings,
        message="Document scanned and perspective-corrected successfully.",
        diagnostics=diag_data if include_diagnostics else None
    )

@app.post("/api/export/pdf")
async def export_pdf_endpoint(
    file: Optional[UploadFile] = File(None),
    image_data: Optional[str] = Form(None),
    title: str = Form("SmartScan Document")
):
    """
    Exports a scanned document image as a high quality PDF file.
    """
    if file is not None:
        file_bytes = await file.read()
        image_rgb, _, _ = validate_and_decode_image(file_bytes)
    elif image_data is not None:
        image_rgb = decode_base64_to_image(image_data)
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Image data is required for PDF export."
        )

    pdf_bytes = export_image_to_pdf(image_rgb, title=title)

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": 'attachment; filename="document_scanned.pdf"'
        }
    )
