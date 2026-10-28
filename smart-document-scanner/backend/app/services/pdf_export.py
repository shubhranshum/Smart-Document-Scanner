import io
from typing import Optional
from PIL import Image
import numpy as np
from reportlab.lib.pagesizes import letter, A4
from reportlab.pdfgen import canvas

def export_image_to_pdf(image_rgb: np.ndarray, title: str = "SmartScan Document") -> bytes:
    """
    Exports an RGB numpy array image into a standard A4 formatted PDF document bytes.
    The image is centered and scaled to preserve aspect ratio within margins.
    """
    h, w = image_rgb.shape[:2]
    pil_img = Image.fromarray(image_rgb)

    # Save to in-memory buffer
    img_byte_arr = io.BytesIO()
    pil_img.save(img_byte_arr, format="JPEG", quality=95)
    img_byte_arr.seek(0)

    pdf_buffer = io.BytesIO()
    
    # Use A4 page size
    page_w, page_h = A4
    margin = 36.0  # 0.5 inch margin

    printable_w = page_w - 2 * margin
    printable_h = page_h - 2 * margin

    # Calculate scale to fit on page while maintaining aspect ratio
    scale = min(printable_w / float(w), printable_h / float(h))
    draw_w = w * scale
    draw_h = h * scale

    # Center image
    x_pos = margin + (printable_w - draw_w) / 2.0
    y_pos = margin + (printable_h - draw_h) / 2.0

    c = canvas.Canvas(pdf_buffer, pagesize=A4)
    c.setTitle(title)
    c.setAuthor("SmartScan Document Scanner")
    c.setSubject("Document Perspective Correction & Enhancement")

    # Draw image from PIL in-memory data
    from reportlab.lib.utils import ImageReader
    reader = ImageReader(img_byte_arr)
    c.drawImage(reader, x_pos, y_pos, width=draw_w, height=draw_h, preserveAspectRatio=True)
    c.showPage()
    c.save()

    pdf_buffer.seek(0)
    return pdf_buffer.getvalue()
