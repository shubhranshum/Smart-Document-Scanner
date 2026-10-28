import io
import pytest
import numpy as np
from PIL import Image
from fastapi import HTTPException
from app.services.image_validation import (
    validate_and_decode_image,
    encode_image_to_base64,
    decode_base64_to_image
)

def create_test_image_bytes(width=200, height=150, color=(100, 150, 200), fmt="JPEG"):
    img = Image.new("RGB", (width, height), color=color)
    buf = io.BytesIO()
    img.save(buf, format=fmt)
    return buf.getvalue()

def test_valid_image_decoding():
    raw_bytes = create_test_image_bytes(300, 200)
    arr, w, h = validate_and_decode_image(raw_bytes)
    assert w == 300
    assert h == 200
    assert arr.shape == (200, 300, 3)
    assert arr.dtype == np.uint8

def test_empty_image_raises_error():
    with pytest.raises(HTTPException) as exc:
        validate_and_decode_image(b"")
    assert exc.value.status_code == 400

def test_corrupt_image_bytes_raises_error():
    with pytest.raises(HTTPException) as exc:
        validate_and_decode_image(b"not-an-image-data-just-random-garbage")
    assert exc.value.status_code == 400

def test_base64_encode_decode_roundtrip():
    orig_arr = np.zeros((100, 150, 3), dtype=np.uint8)
    orig_arr[:, :] = [50, 120, 200]

    b64_str = encode_image_to_base64(orig_arr, format="PNG")
    assert b64_str.startswith("data:image/png;base64,")

    decoded_arr = decode_base64_to_image(b64_str)
    assert decoded_arr.shape == orig_arr.shape
    # Lossless PNG roundtrip check
    np.testing.assert_array_equal(orig_arr, decoded_arr)
