import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List

class Settings(BaseSettings):
    app_name: str = "Smart Document Scanner API"
    backend_version: str = "1.0.0"
    debug: bool = False
    
    # CORS (allows local dev and deployed Vercel domains)
    allowed_origins: List[str] = [
        "*",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:5173",
        "http://127.0.0.1:5173"
    ]
    
    # Upload limits
    max_upload_size_bytes: int = 15 * 1024 * 1024  # 15 MB
    max_image_pixels: int = 25_000_000              # 25 Megapixels limit
    max_output_pixels: int = 16_000_000             # 16 Megapixels limit for perspective warp
    
    # Detection parameters
    detection_target_dim: int = 1000                # Dimension to resize to for edge detection
    min_document_area_ratio: float = 0.05           # Contour must be at least 5% of image area
    approx_poly_epsilon_ratio: float = 0.02         # approxPolyDP perimeter ratio
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()
