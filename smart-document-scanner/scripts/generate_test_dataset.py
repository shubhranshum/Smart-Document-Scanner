import os
import json
import numpy as np
import cv2

def create_synthetic_page(width=500, height=700, title="DOCUMENT SCAN TEST"):
    """
    Creates a clean, rendered document page with title, text lines, table, and border.
    """
    page = np.full((height, width, 3), 248, dtype=np.uint8)

    # Add outer page margin border
    cv2.rectangle(page, (20, 20), (width - 20, height - 20), (220, 220, 220), 1)

    # Document Header Title
    cv2.putText(page, title, (40, 70), cv2.FONT_HERSHEY_DUPLEX, 0.9, (20, 20, 20), 2, cv2.LINE_AA)
    cv2.line(page, (40, 85), (width - 40, 85), (40, 40, 40), 2)

    # Text lines simulation
    y = 120
    np.random.seed(42)
    while y < height - 140:
        # Paragraph header or standard text line
        line_len = np.random.randint(width // 2, width - 80)
        line_thickness = 1 if y % 60 != 0 else 2
        color = (50, 50, 50) if line_thickness == 1 else (20, 20, 20)
        cv2.line(page, (40, y), (40 + line_len, y), color, line_thickness)
        y += np.random.randint(18, 26)

    # Small table / signature block at bottom
    cv2.rectangle(page, (40, height - 110), (width - 40, height - 40), (180, 180, 180), 1)
    cv2.putText(page, "VERIFIED OFFICIAL COPY", (60, height - 75), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (80, 80, 80), 1)

    return page

def create_background(bg_type: str, w: int, h: int) -> np.ndarray:
    """
    Creates various contrasting backgrounds (slate, wood, gradient, texture).
    """
    if bg_type == "slate":
        bg = np.full((h, w, 3), (35, 38, 45), dtype=np.uint8)
        # Add subtle noise
        noise = np.random.randint(-8, 8, (h, w, 3), dtype=np.int16)
        return np.clip(bg.astype(np.int16) + noise, 0, 255).astype(np.uint8)

    elif bg_type == "wood":
        # Horizontal wood grain tone
        base_color = np.array([40, 65, 110], dtype=np.float32)  # Brownish
        bg = np.tile(base_color, (h, w, 1))
        # Grain variation across Y
        grain = (np.sin(np.linspace(0, 50, h)) * 15).reshape(h, 1, 1)
        bg = np.clip(bg + grain, 0, 255).astype(np.uint8)
        return bg

    elif bg_type == "gradient":
        # Diagonal lighting gradient
        x = np.linspace(0, 1, w)
        y = np.linspace(0, 1, h)
        xx, yy = np.meshgrid(x, y)
        grad = (xx + yy) / 2.0
        r = np.clip(40 + grad * 50, 0, 255)
        g = np.clip(50 + grad * 50, 0, 255)
        b = np.clip(60 + grad * 60, 0, 255)
        return np.dstack((r, g, b)).astype(np.uint8)

    else:
        # Default dark neutral
        return np.full((h, w, 3), 50, dtype=np.uint8)

def apply_lighting_gradient(image: np.ndarray, light_type: str) -> np.ndarray:
    """
    Simulates real-world non-uniform ambient illumination.
    """
    h, w = image.shape[:2]
    if light_type == "vignette":
        # Darkened corners
        X = cv2.getGaussianKernel(w, w / 2)
        Y = cv2.getGaussianKernel(h, h / 2)
        kernel = Y * X.T
        mask = kernel / kernel.max()
        # Scale mask to 0.7 .. 1.0
        mask = 0.7 + 0.3 * mask
        return np.clip(image.astype(np.float32) * mask[:, :, np.newaxis], 0, 255).astype(np.uint8)

    elif light_type == "corner_shadow":
        # Shadow from top-left
        x = np.linspace(0.6, 1.0, w)
        y = np.linspace(0.6, 1.0, h)
        xx, yy = np.meshgrid(x, y)
        mask = (xx * yy)[:, :, np.newaxis]
        return np.clip(image.astype(np.float32) * mask, 0, 255).astype(np.uint8)

    return image

def generate_test_cases():
    test_cases = [
        {
            "id": "doc_01_mild_angle_slate",
            "bg": "slate",
            "lighting": "even",
            "corners": [[180, 120], [820, 140], [790, 880], [150, 850]],
            "doc_size": (500, 700),
            "title": "ANNUAL FINANCIAL REPORT 2026",
            "description": "Mild perspective tilt on slate background"
        },
        {
            "id": "doc_02_moderate_angle_wood",
            "bg": "wood",
            "lighting": "even",
            "corners": [[140, 180], [860, 100], [820, 920], [100, 820]],
            "doc_size": (500, 700),
            "title": "RESEARCH MANUSCRIPT DRAFT",
            "description": "Moderate rotational perspective on wooden surface"
        },
        {
            "id": "doc_03_steep_perspective_gradient",
            "bg": "gradient",
            "lighting": "vignette",
            "corners": [[280, 160], [740, 150], [920, 860], [100, 840]],
            "doc_size": (500, 680),
            "title": "CERTIFICATE OF MERIT",
            "description": "Steep trapezoidal perspective with vignette lighting"
        },
        {
            "id": "doc_04_skewed_left_slate",
            "bg": "slate",
            "lighting": "corner_shadow",
            "corners": [[120, 100], [780, 190], [840, 870], [200, 900]],
            "doc_size": (500, 720),
            "title": "UNIVERSITY SYLLABUS IPCV",
            "description": "Asymmetric camera tilt with corner shadow"
        },
        {
            "id": "doc_05_landscape_wood",
            "bg": "wood",
            "lighting": "even",
            "corners": [[160, 220], [840, 180], [800, 800], [120, 840]],
            "doc_size": (700, 500),
            "title": "SYSTEM ARCHITECTURE BLUEPRINT",
            "description": "Landscape oriented document on textured background"
        },
        {
            "id": "doc_06_compact_receipt_gradient",
            "bg": "gradient",
            "lighting": "even",
            "corners": [[260, 200], [720, 220], [680, 820], [220, 780]],
            "doc_size": (400, 600),
            "title": "PURCHASE INVOICE #98214",
            "description": "Centered invoice with clear high contrast margins"
        },
        {
            "id": "doc_07_strong_vignette_slate",
            "bg": "slate",
            "lighting": "vignette",
            "corners": [[200, 150], [800, 170], [750, 860], [180, 820]],
            "doc_size": (500, 700),
            "title": "LEGAL CONTRACT AGREEMENT",
            "description": "Vignette shadow testing adaptive binarization"
        },
        {
            "id": "doc_08_rotated_diamond_wood",
            "bg": "wood",
            "lighting": "corner_shadow",
            "corners": [[220, 120], [850, 260], [730, 920], [120, 760]],
            "doc_size": (520, 680),
            "title": "EXAMINATION ADMIT CARD",
            "description": "Noticeable clockwise rotational angle"
        },
        {
            "id": "doc_09_wide_panoramic_slate",
            "bg": "slate",
            "lighting": "even",
            "corners": [[130, 240], [880, 200], [850, 760], [90, 800]],
            "doc_size": (720, 480),
            "title": "WIDE CERTIFICATE OF COMPLETION",
            "description": "Wide aspect ratio document"
        },
        {
            "id": "doc_10_high_angle_gradient",
            "bg": "gradient",
            "lighting": "even",
            "corners": [[310, 180], [710, 190], [860, 850], [150, 840]],
            "doc_size": (480, 680),
            "title": "MATHEMATICAL FORMULAS COMPENDIUM",
            "description": "Top-down angled perspective projection"
        }
    ]
    return test_cases

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.join(script_dir, ".."))
    sample_images_dir = os.path.join(project_root, "dataset", "sample_images")
    ground_truth_dir = os.path.join(project_root, "dataset", "ground_truth")

    os.makedirs(sample_images_dir, exist_ok=True)
    os.makedirs(ground_truth_dir, exist_ok=True)

    canvas_w, canvas_h = 1000, 1000
    test_cases = generate_test_cases()
    ground_truth_records = {}

    print(f"Generating {len(test_cases)} synthetic test images with verified ground truth...")

    for tc in test_cases:
        tc_id = tc["id"]
        doc_w, doc_h = tc["doc_size"]

        # 1. Generate clean unwarped document
        doc_img = create_synthetic_page(doc_w, doc_h, title=tc["title"])

        # Source corners: rectangle [TL, TR, BR, BL]
        src_pts = np.array([
            [0, 0],
            [doc_w - 1, 0],
            [doc_w - 1, doc_h - 1],
            [0, doc_h - 1]
        ], dtype=np.float32)

        # Destination corners in scene canvas [TL, TR, BR, BL]
        dst_pts = np.array(tc["corners"], dtype=np.float32)

        # 2. Compute homography mapping document to canvas
        H = cv2.getPerspectiveTransform(src_pts, dst_pts)

        # 3. Create canvas background
        canvas = create_background(tc["bg"], canvas_w, canvas_h)

        # 4. Warp document into canvas
        warped_doc = cv2.warpPerspective(doc_img, H, (canvas_w, canvas_h))

        # Create mask of warped document
        doc_mask = np.zeros((doc_h, doc_w), dtype=np.uint8)
        cv2.rectangle(doc_mask, (0, 0), (doc_w, doc_h), 255, -1)
        warped_mask = cv2.warpPerspective(doc_mask, H, (canvas_w, canvas_h))

        # 5. Composite warped document over background
        mask_bool = warped_mask > 128
        canvas[mask_bool] = warped_doc[mask_bool]

        # 6. Apply lighting model
        final_image = apply_lighting_gradient(canvas, tc["lighting"])

        # 7. Save image file
        filename = f"{tc_id}.jpg"
        filepath = os.path.join(sample_images_dir, filename)
        cv2.imwrite(filepath, final_image, [int(cv2.IMWRITE_JPEG_QUALITY), 95])

        # Record exact ground truth corners
        ground_truth_records[filename] = {
            "id": tc_id,
            "filename": filename,
            "description": tc["description"],
            "image_width": canvas_w,
            "image_height": canvas_h,
            "ground_truth_corners": [
                {"label": "TL", "x": float(tc["corners"][0][0]), "y": float(tc["corners"][0][1])},
                {"label": "TR", "x": float(tc["corners"][1][0]), "y": float(tc["corners"][1][1])},
                {"label": "BR", "x": float(tc["corners"][2][0]), "y": float(tc["corners"][2][1])},
                {"label": "BL", "x": float(tc["corners"][3][0]), "y": float(tc["corners"][3][1])},
            ]
        }
        print(f" -> Generated {filename}: {tc['description']}")

    # Save ground truth JSON
    gt_json_path = os.path.join(ground_truth_dir, "ground_truth.json")
    with open(gt_json_path, "w", encoding="utf-8") as f:
        json.dump(ground_truth_records, f, indent=2)

    print(f"\nSuccessfully generated {len(test_cases)} images in: {sample_images_dir}")
    print(f"Ground truth catalog saved to: {gt_json_path}")

if __name__ == "__main__":
    main()
