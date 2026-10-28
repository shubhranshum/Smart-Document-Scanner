from typing import Optional
import cv2
import numpy as np
from app.schemas import EnhancementMode

def enhance_image(
    image_rgb: np.ndarray,
    mode: EnhancementMode = EnhancementMode.COLOR,
    adaptive_block_size: int = 21,
    adaptive_c: int = 10,
    clahe_clip_limit: float = 2.5,
    clahe_tile_grid: int = 8
) -> np.ndarray:
    """
    Applies the specified document enhancement technique to the perspective-corrected image.
    Modes:
      - 'color': Unaltered color image.
      - 'grayscale': Converted to clean grayscale (returned as 3-channel RGB for consistency).
      - 'black_white': Adaptive thresholding for crisp, high-contrast text scanning.
      - 'contrast': CLAHE on the L-channel of LAB color space, improving contrast while preserving natural colors.
    """
    if mode == EnhancementMode.COLOR or mode == "color":
        return image_rgb.copy()

    elif mode == EnhancementMode.GRAYSCALE or mode == "grayscale":
        if len(image_rgb.shape) == 3:
            gray = cv2.cvtColor(image_rgb, cv2.COLOR_RGB2GRAY)
        else:
            gray = image_rgb.copy()
        # Convert to 3-channel RGB for uniform image encoding/saving
        return cv2.cvtColor(gray, cv2.COLOR_GRAY2RGB)

    elif mode == EnhancementMode.BLACK_WHITE or mode == "black_white":
        if len(image_rgb.shape) == 3:
            gray = cv2.cvtColor(image_rgb, cv2.COLOR_RGB2GRAY)
        else:
            gray = image_rgb.copy()

        # Slight Gaussian blur to reduce high-frequency noise before thresholding
        blurred = cv2.GaussianBlur(gray, (3, 3), 0)

        # Ensure block size is odd and >= 3
        b_size = adaptive_block_size if adaptive_block_size % 2 == 1 else adaptive_block_size + 1
        b_size = max(3, b_size)

        bw = cv2.adaptiveThreshold(
            blurred,
            255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY,
            b_size,
            adaptive_c
        )
        return cv2.cvtColor(bw, cv2.COLOR_GRAY2RGB)

    elif mode == EnhancementMode.CONTRAST or mode == "contrast":
        if len(image_rgb.shape) == 3:
            # Convert to LAB color space
            lab = cv2.cvtColor(image_rgb, cv2.COLOR_RGB2LAB)
            l_channel, a_channel, b_channel = cv2.split(lab)

            # Apply CLAHE to L-channel
            clahe = cv2.createCLAHE(
                clipLimit=clahe_clip_limit,
                tileGridSize=(clahe_tile_grid, clahe_tile_grid)
            )
            l_enhanced = clahe.apply(l_channel)

            # Merge channels and convert back to RGB
            lab_enhanced = cv2.merge((l_enhanced, a_channel, b_channel))
            return cv2.cvtColor(lab_enhanced, cv2.COLOR_LAB2RGB)
        else:
            clahe = cv2.createCLAHE(clipLimit=clahe_clip_limit, tileGridSize=(clahe_tile_grid, clahe_tile_grid))
            enhanced = clahe.apply(image_rgb)
            return cv2.cvtColor(enhanced, cv2.COLOR_GRAY2RGB)

    else:
        # Fallback to original
        return image_rgb.copy()
