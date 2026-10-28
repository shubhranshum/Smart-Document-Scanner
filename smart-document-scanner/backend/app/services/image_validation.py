import io
import base64
from typing import Tuple
from PIL import Image, ImageOps
import numpy as np
import cv2
from fastapi import HTTPException, status
from app.config import settings

def validate_and_decode_image(file_bytes: bytes) -> Tuple[np.ndarray, int, int]:
    """
    Validates the uploaded file size and content, decodes image bytes,
    normalizes EXIF orientation, and returns an RGB numpy array along with width and height.
    """
    if not file_bytes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Empty image file received."
        )

    if len(file_bytes) > settings.max_upload_size_bytes:
        max_mb = settings.max_upload_size_bytes // (1024 * 1024)
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"Image file exceeds maximum allowed size of {max_mb} MB."
        )

    try:
        pil_img = Image.open(io.BytesIO(file_bytes))
        pil_img.verify()
        # verify() closes the file or clears tile data, reopen for processing
        pil_img = Image.open(io.BytesIO(file_bytes))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid or corrupted image file: {str(e)}"
        )

    # Handle EXIF orientation (essential for camera phone photos)
    try:
        pil_img = ImageOps.exif_transpose(pil_img)
    except Exception:
        pass  # If no EXIF or transpose fails, proceed with raw image

    # Convert to RGB (handles RGBA, Palette, Grayscale, etc.)
    if pil_img.mode != "RGB":
        pil_img = pil_img.convert("RGB")

    width, height = pil_img.size

    if width <= 0 or height <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Decoded image has non-positive dimensions."
        )

    total_pixels = width * height
    if total_pixels > settings.max_image_pixels:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Image dimension ({width}x{height}) exceeds maximum pixel limit of {settings.max_image_pixels}."
        )

    img_rgb = np.array(pil_img, dtype=np.uint8)
    return img_rgb, width, height

def encode_image_to_base64(image_rgb: np.ndarray, format: str = "PNG") -> str:
    """
    Encodes an RGB numpy array to a base64 Data URL (e.g. data:image/png;base64,...).
    """
    # Convert RGB to BGR for cv2.imencode
    if len(image_rgb.shape) == 2:
        img_to_encode = image_rgb
    else:
        img_to_encode = cv2.cvtColor(image_rgb, cv2.COLOR_RGB2BGR)

    ext = f".{format.lower()}"
    success, buffer = cv2.imencode(ext, img_to_encode)
    if not success:
        raise RuntimeError(f"Failed to encode image to {format}")

    b64_bytes = base64.b64encode(buffer).decode("utf-8")
    mime_type = "image/png" if format.upper() == "PNG" else "image/jpeg"
    return f"data:{mime_type};base64,{b64_bytes}"

def decode_base64_to_image(data_url_or_b64: str) -> np.ndarray:
    """
    Decodes a base64 string or data URL to an RGB numpy array.
    """
    if "," in data_url_or_b64:
        _, b64_str = data_url_or_b64.split(",", 1)
    else:
        b64_str = data_url_or_b64

    try:
        img_bytes = base64.b64decode(b64_str)
        pil_img = Image.open(io.BytesIO(img_bytes))
        if pil_img.mode != "RGB":
            pil_img = pil_img.convert("RGB")
        return np.array(pil_img, dtype=np.uint8)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to decode base64 image data: {str(e)}"
        )
