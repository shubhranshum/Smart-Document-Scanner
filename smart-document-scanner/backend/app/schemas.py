from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class Point(BaseModel):
    x: float
    y: float

class EnhancementMode(str, Enum):
    COLOR = "color"
    GRAYSCALE = "grayscale"
    BLACK_WHITE = "black_white"
    CONTRAST = "contrast"

class HealthResponse(BaseModel):
    status: str
    opencv_version: str
    backend_version: str

class DetectionResponse(BaseModel):
    detected: bool
    corners: Optional[List[Point]] = None
    method: Optional[str] = None
    contour_area: Optional[float] = None
    contour_perimeter: Optional[float] = None
    image_width: int
    image_height: int
    processing_time_ms: float
    preview_image: Optional[str] = None
    message: Optional[str] = None
    diagnostics: Optional[Dict[str, Any]] = None

class CorrectionResponse(BaseModel):
    corrected_image: str
    output_width: int
    output_height: int
    processing_time_ms: float
    metadata: Optional[Dict[str, Any]] = None

class EnhanceResponse(BaseModel):
    enhanced_image: str
    mode: str
    output_width: int
    output_height: int
    processing_time_ms: float

class ProcessResponse(BaseModel):
    detected: bool
    corners: Optional[List[Point]] = None
    annotated_preview: Optional[str] = None
    corrected_image: Optional[str] = None
    enhanced_image: Optional[str] = None
    output_width: Optional[int] = None
    output_height: Optional[int] = None
    detection_method: Optional[str] = None
    enhancement_mode: Optional[str] = None
    processing_time_ms: float
    warnings: List[str] = []
    message: Optional[str] = None
    diagnostics: Optional[Dict[str, Any]] = None
