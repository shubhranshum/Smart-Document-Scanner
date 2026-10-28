# Project Report: Smart Document Scanner Using Image Processing and Perspective Correction

---

## 1. Title Page

**Project Title:** Smart Document Scanner: Document Detection and Perspective Correction Using Image Processing  
**Course:** Image Processing and Computer Vision (IPCV)  
**Academic Year:** 2026–2027  
**Technology Stack:** Python 3.12, OpenCV 4.11, NumPy, FastAPI, React 18, Vite, Tailwind CSS  
**Authors:** Undergraduate Project Team  

---

## 2. Abstract

In digital document management, mobile photography is the dominant method for digitizing paper records, receipts, whiteboards, and contracts. However, mobile photographs suffer from arbitrary shooting angles, projective distortion (keystone effect), optical perspective warping, uneven illumination, and background clutter. 

This project presents **SmartScan**, an explainable, end-to-end Image Processing and Computer Vision system for automated document boundary detection, homography-based perspective rectification, and visual readability enhancement. Unlike black-box neural approaches that demand significant compute and lack mathematical explainability, SmartScan employs classical differential edge detection (Canny), morphological boundary consolidation, topological contour extraction (Suzuki algorithm), Douglas-Peucker polygonal approximation, and 8-DOF planar homography transformation via Singular Value Decomposition (SVD). 

The system features an interactive, web-based graphical user interface built with React and FastAPI, incorporating a robust manual corner adjustment fallback mechanism to overcome severe environmental ambiguities. On an evaluation benchmark with mathematically verified ground truth, the system achieved a 100% detection success rate with a mean corner Euclidean error of 1.41 pixels (0.100% normalized error) and an average processing latency of 4.11 ms.

---

## 3. Introduction

Document digitization is fundamental to modern information retrieval, administrative workflows, and optical character recognition (OCR). Traditional flatbed optical scanners produce rectilinear, high-contrast, uniformly illuminated raster images. Conversely, handheld smartphone cameras introduce non-orthogonal viewing angles, resulting in quadrilateral distortions where parallel document edges converge toward vanishing points.

To make handheld document photographs suitable for archiving, printing, and OCR extraction, the quadrilateral document region must be identified, isolated from the surrounding scene, and transformed into a canonical front-facing rectangular image. This project implements a fully functional web application demonstrating the mathematical and practical aspects of digital image processing and 2D projective geometry.

---

## 4. Problem Statement

Photographs of documents captured in uncontrolled real-world environments exhibit several physical and computational challenges:
1. **Perspective Distortion:** When the camera optical axis is not strictly perpendicular to the document plane, rectangular sheets project as irregular quadrilaterals.
2. **Background Clutter & Edge Noise:** Desktops, textures (wood grain, marble), stationery, and shadows introduce extraneous gradient vectors.
3. **Non-Uniform Ambient Lighting:** Shadows cast by the user’s hand, phone body, or ceiling lights generate localized intensity gradients that degrade global thresholding methods.
4. **Scale & Resolution Variations:** Mobile sensors capture images ranging from 2 megapixels to over 50 megapixels, necessitating scale-invariant processing pipelines.
5. **Algorithmic Edge Cases:** Classical edge detection may fail under low-contrast boundaries (e.g., white document on white desk), requiring seamless user-in-the-loop fallback mechanisms.

---

## 5. Objectives

The primary objectives of this project are:
- To design a modular image-processing pipeline capable of detecting document boundaries without deep neural network dependencies.
- To formulate and apply 2D planar projective transformations (Homography) to rectify perspective distortion.
- To implement adaptive thresholding and contrast-limited adaptive histogram equalization (CLAHE) to restore text legibility.
- To create a reactive, professional web application enabling real-time preview, SVG-based manual corner refinement, side-by-side comparison, and PDF export.
- To establish a reproducible benchmarking framework evaluating corner localization error and latency against synthetic ground truth.

---

## 6. Scope

The scope of this project encompasses:
- Single-page rectangular planar documents (sheets, business cards, receipts, books lying flat).
- Input image formats: JPEG, PNG, WEBP up to 15 MB.
- Interactive web interface operable across desktop and mobile browsers.
- Quantitative benchmarking using normalized Euclidean corner error.
- Purely local, reproducible execution without paid cloud APIs or proprietary external dependencies.

*Out of Scope:* 3D curved surface unwarping (e.g., thick bound book curved spines), continuous video stream tracking, and commercial multi-page batch OCR ingestion.

---

## 7. Existing Approaches and Limitations

| Approach | Working Principle | Strengths | Limitations |
| :--- | :--- | :--- | :--- |
| **Flatbed Scanners** | Physical linear CCD sensor array sweep | Perfect orthogonal projection, uniform lighting | Bulky, non-portable, slow, unable to scan books or large posters |
| **Deep Learning (e.g., YOLO / U-Net)** | CNN/Transformer bounding segmentation | Handles complex cluttered backgrounds | Opaque reasoning, requires massive labeled training datasets, high memory/GPU footprint |
| **Naive Classical Contours** | Single-threshold Canny + largest area contour | Fast, lightweight, explainable | Fragile to shadow edges, fails if document is not the largest object, prone to self-intersecting approximations |

SmartScan bridges these gaps by utilizing a **multi-stage adaptive fallback pipeline** coupled with an interactive **SVG-based manual corner adjustment workspace**.

---

## 8. Proposed Methodology

The SmartScan processing pipeline is structured into discrete, testable stages:

```
[ Input Photo ] 
       │
       ▼
[ EXIF Transpose & Pixel Validation ]
       │
       ▼
[ Aspect-Preserving Dimension Normalization (Target = 1000px) ]
       │
       ▼
[ Grayscale Conversion -> Gaussian Filter (5x5, σ = 1.4) ]
       │
       ▼
[ Multi-Stage Edge Extraction ]
   ├── Stage 1: Auto-Otsu / Median Canny
   ├── Stage 2: Sensitive Dual-Threshold Canny
   └── Stage 3: Adaptive Gaussian Thresholding
       │
       ▼
[ Suzuki Contour Hierarchy & Area Filtering (> 5% Total Canvas) ]
       │
       ▼
[ Douglas-Peucker Polygonal Approximation (ε = 0.02 * Perimeter) ]
       │
       ▼
[ Convexity Verification & No-Self-Intersection Geometry Checks ]
       │
       ▼
[ Deterministic Clockwise Corner Ordering: [TL, TR, BR, BL] ]
       │
       ▼
[ Direct Linear Transformation (DLT) Planar Homography Warping ]
       │
       ▼
[ Post-Warp Enhancement: Color / Grayscale / Adaptive B&W / CLAHE ]
       │
       ▼
[ Rectified Output Image / PDF Export ]
```

---

## 9. System Architecture

SmartScan is architected as a decoupled client-server web system:

```
┌─────────────────────────────────────────────────────────────┐
│                       Client (React)                        │
│                                                             │
│  ┌──────────────┐   ┌───────────────┐   ┌────────────────┐  │
│  │ UploadPanel  │   │ CornerEditor  │   │ ImageWorkspace │  │
│  └──────┬───────┘   └───────┬───────┘   └────────┬───────┘  │
│         │                   │                    │          │
│  ┌──────┴───────────────────┴────────────────────┴───────┐  │
│  │         useDocumentScanner Custom Hook State          │  │
│  └──────────────────────────┬────────────────────────────┘  │
│                             │ REST API (JSON / Multipart)   │
└─────────────────────────────┼───────────────────────────────┘
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    Backend Server (FastAPI)                 │
│                                                             │
│  ┌───────────────────────────────────────────────────────┐  │
│  │                    API Router (main.py)               │  │
│  │    /api/health   /api/detect   /api/correct  /api/pdf │  │
│  └──────────────────────────┬────────────────────────────┘  │
│                             │                               │
│  ┌──────────────────────────┴────────────────────────────┐  │
│  │                 Computer Vision Services              │  │
│  │  • image_validation.py  • preprocessing.py            │  │
│  │  • document_detection.py • perspective.py             │  │
│  │  • enhancement.py       • pdf_export.py               │  │
│  └───────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

---

## 10. Functional Requirements

1. **Image Ingestion:** Accept user upload via file picker or drag-and-drop for JPG, PNG, and WEBP formats up to 15 MB.
2. **Dimension & EXIF Normalization:** Automatically correct mobile camera EXIF orientation tags.
3. **Automated Boundary Detection:** Detect the 4 document corners without user guidance.
4. **Visual Corner Overlay:** Render an annotated SVG overlay displaying the detected polygon and labeled corner handles (TL, TR, BR, BL).
5. **Interactive Corner Adjustment:** Enable draggable corner manipulation and manual 4-point click mode for edge cases.
6. **Perspective Correction:** Straighten quadrilateral regions into an orthogonal rectangular frame using bicubic interpolation.
7. **Document Filtering:** Provide 4 distinct enhancement modes: Original Color, Grayscale, Adaptive Black & White, and CLAHE Contrast.
8. **Comparison View:** Side-by-side and interactive split slider comparing input and corrected images.
9. **Export & Download:** Generate direct PNG image downloads and formatted A4 PDF files.

---

## 11. Non-Functional Requirements

- **Latency:** End-to-end detection and warping execution time below 100 ms for 4K source photographs.
- **Explainability:** All geometric and filter transformations must adhere to deterministic, publishable mathematical formulas.
- **Portability:** Containerless execution on standard consumer hardware across macOS, Linux, and Windows.
- **Robustness:** Graceful error handling for corrupt byte streams, non-document scenes, and collinear corner coordinates.

---

## 12. Algorithm Design

### 12.1 Image Downsampling for Detection
Mobile photographs frequently exceed 4000x3000 pixels. Performing differential operators at this resolution is computationally expensive and sensitive to microscopic paper textures. The system downsamples the image such that $\max(W, H) \le 1000$, computing scale factors:
$$s_x = \frac{W_{\text{resized}}}{W_{\text{orig}}}, \quad s_y = \frac{H_{\text{resized}}}{H_{\text{orig}}}$$
Detected corner coordinates $(x_r, y_r)$ are mapped back to original resolution via:
$$x_{\text{orig}} = \frac{x_r}{s_x}, \quad y_{\text{orig}} = \frac{y_r}{s_y}$$

### 12.2 Gaussian Smoothing
To attenuate high-frequency noise prior to gradient estimation, a 2D Gaussian kernel $G(x, y)$ of size $5 \times 5$ is convolved with the grayscale intensity array:
$$I_{\text{smooth}}(x, y) = I_{\text{gray}}(x, y) * G(x, y)$$

### 12.3 Canny Edge Detection
Gradient magnitudes and orientations are computed using $3 \times 3$ Sobel masks:
$$G = \sqrt{I_x^2 + I_y^2}, \quad \theta = \arctan\left(\frac{I_y}{I_x}\right)$$
Non-maximum suppression retains only pixels that are local maxima along the gradient direction $\theta$. Hysteresis thresholding uses dynamic thresholds $T_{\text{low}}$ and $T_{\text{high}}$ derived from median pixel intensity.

### 12.4 Contour Extraction and Douglas-Peucker Approximation
Continuous closed contours $C = \{p_1, p_2, \dots, p_n\}$ are extracted via `cv2.findContours`. Contours with enclosed area $A(C) < 0.05 \cdot (W \cdot H)$ are pruned. For remaining candidates, the Douglas-Peucker algorithm iteratively simplifies the polygon:
$$d_{\max} \le \epsilon = 0.02 \cdot \text{arcLength}(C, \text{true})$$
If the simplified contour contains exactly 4 vertices, it undergoes convexity validation:
$$\text{isContourConvex}(\text{approx}) = \text{true}$$

---

## 13. Mathematical Explanation of Homography

Planar perspective transformation establishes a mapping between points on the document plane $\mathbf{x} = [x, y, 1]^T$ and corresponding points in the rectified image plane $\mathbf{x}' = [x', y', 1]^T$ using a non-singular $3 \times 3$ projective matrix $\mathbf{H}$:

$$\begin{bmatrix} x' \\ y' \\ 1 \end{bmatrix} \sim \mathbf{H} \begin{bmatrix} x \\ y \\ 1 \end{bmatrix} = \begin{bmatrix} h_{11} & h_{12} & h_{13} \\ h_{21} & h_{22} & h_{23} \\ h_{31} & h_{32} & h_{33} \end{bmatrix} \begin{bmatrix} x \\ y \\ 1 \end{bmatrix}$$

Expanding the homogeneous system yields inhomogeneous Cartesian coordinates:
$$x' = \frac{h_{11}x + h_{12}y + h_{13}}{h_{31}x + h_{32}y + h_{33}}, \quad y' = \frac{h_{21}x + h_{22}y + h_{23}}{h_{31}x + h_{32}y + h_{33}}$$

Because $\mathbf{H}$ is defined up to an arbitrary non-zero scale factor, it possesses 8 degrees of freedom (DOF). Each point correspondence provides 2 independent linear constraints:
$$\begin{aligned}
h_{11}x + h_{12}y + h_{13} - x'(h_{31}x + h_{32}y + h_{33}) &= 0 \\
h_{21}x + h_{22}y + h_{23} - y'(h_{31}x + h_{32}y + h_{33}) &= 0
\end{aligned}$$

With 4 non-collinear point correspondences, we construct an $8 \times 9$ linear system $\mathbf{A} \mathbf{h} = \mathbf{0}$, where:
$$\mathbf{A}_i = \begin{bmatrix} 
x_i & y_i & 1 & 0 & 0 & 0 & -x_i x'_i & -y_i x'_i & -x'_i \\
0 & 0 & 0 & x_i & y_i & 1 & -x_i y'_i & -y_i y'_i & -y'_i 
\end{bmatrix}$$

The solution vector $\mathbf{h}$ is the right singular vector of $\mathbf{A}$ corresponding to the smallest singular value, determined via Singular Value Decomposition (SVD).

### Destination Dimension Calculation
The rectified rectangle dimensions $(W_{\text{dst}}, H_{\text{dst}})$ are derived from Euclidean edge norms:
$$W_{\text{top}} = \|\mathbf{p}_{\text{TR}} - \mathbf{p}_{\text{TL}}\|_2, \quad W_{\text{bottom}} = \|\mathbf{p}_{\text{BR}} - \mathbf{p}_{\text{BL}}\|_2 \implies W_{\text{dst}} = \max(W_{\text{top}}, W_{\text{bottom}})$$
$$H_{\text{left}} = \|\mathbf{p}_{\text{BL}} - \mathbf{p}_{\text{TL}}\|_2, \quad H_{\text{right}} = \|\mathbf{p}_{\text{BR}} - \mathbf{p}_{\text{TR}}\|_2 \implies H_{\text{dst}} = \max(H_{\text{left}}, H_{\text{right}})$$

---

## 14. Implementation Details

- **Backend Architecture:** Built with FastAPI 0.119 and Python 3.12, utilizing typed Pydantic models for request/response validation.
- **Image Operations:** Executed in-memory using NumPy arrays and OpenCV 4.11 headless. No user files are stored permanently on server disk.
- **PDF Generation:** Implemented using ReportLab, scaling rectified documents into centered A4 portrait pages with standard print margins.
- **Frontend Architecture:** Single Page Application (SPA) built using React 18 and Vite. State is managed via a custom `useDocumentScanner` hook enforcing guarded state transitions.
- **Corner Editor:** Implemented using an SVG overlay whose coordinate space maps directly to the image’s original resolution, ensuring precision across browser resizing and zoom levels.

---

## 15. Testing Methodology

The system was evaluated through an automated testing suite:
1. **Backend Unit & Integration Tests (19 Test Cases):** Tested using `pytest` and `fastapi.testclient.TestClient`. Evaluated empty uploads, corrupt byte buffers, EXIF tag decoding, convex/concave polygon validation, clockwise sorting, perspective warping dimensions, filter output channel shapes, and end-to-end pipeline execution.
2. **Frontend Component & Utility Tests (8 Test Cases):** Tested using `vitest` and React Testing Library. Validated file type/size enforcement, button disabled states based on pipeline stage, and cross-product convexity validation.
3. **Quantitative Benchmark Framework:** Executed on 10 synthetic test images with known mathematical homographies.

---

## 16. Results and Benchmark Evaluation

The quantitative benchmark was executed using `scripts/evaluate_dataset.py`. Ground truth corner coordinates were compared against detected corners:

| Metric | Target Specification | Measured Result |
| :--- | :--- | :--- |
| **Total Test Cases** | 10 Scenarios | 10 Scenarios |
| **Detection Success Rate** | $\ge 90\%$ | **100.0%** (10/10) |
| **Mean Corner Error** | $\le 5.0$ pixels | **1.41 pixels** |
| **Normalized Corner Error** | $\le 0.5\%$ | **0.100%** |
| **Mean Detection Latency** | $\le 50$ ms | **4.11 ms** |
| **Backend Unit Tests** | 100% Pass | **19 / 19 Passed** |
| **Frontend Unit Tests** | 100% Pass | **8 / 8 Passed** |

*Evaluation Details per Scenario:*
- `doc_01` (Mild Tilt, Slate): Error = 1.41 px, Time = 10.21 ms [PASS]
- `doc_02` (Moderate Angle, Wood): Error = 1.41 px, Time = 3.65 ms [PASS]
- `doc_03` (Steep Perspective, Gradient): Error = 1.41 px, Time = 2.90 ms [PASS]
- `doc_04` (Skewed Left, Shadow): Error = 1.41 px, Time = 3.49 ms [PASS]
- `doc_05` (Landscape, Wood): Error = 1.41 px, Time = 3.73 ms [PASS]
- `doc_06` (Receipt, Gradient): Error = 1.41 px, Time = 3.08 ms [PASS]
- `doc_07` (Vignette Lighting): Error = 1.41 px, Time = 3.98 ms [PASS]
- `doc_08` (Rotated Diamond): Error = 1.41 px, Time = 3.14 ms [PASS]
- `doc_09` (Wide Panoramic): Error = 1.41 px, Time = 4.25 ms [PASS]
- `doc_10` (Top-down Steep Angle): Error = 1.41 px, Time = 2.65 ms [PASS]

---

## 17. Limitations

1. **Low-Contrast Boundaries:** When a white sheet of paper rests on a pure white laminate table, the spatial luminance gradient $\nabla I$ approaches zero, hindering automated edge detection. (Mitigated by manual corner selection).
2. **Non-Planar Documents:** Creased receipts, folded letters, or warped pages violate the 2D planar homography assumption, leading to minor localized barrel or pincushion distortions in the warped output.
3. **Severe Document Occlusion:** If pens, fingers, or coffee mugs obscure one or more document corners, polygonal approximation may detect a 5+ vertex shape.

---

## 18. Future Scope

1. **Mesh-Based Non-Rigid Dewarping:** Integrating Thin Plate Spline (TPS) interpolation or 3D cylindrical surface fitting to rectify curved book pages.
2. **On-Device WebAssembly Inference:** Compiling the OpenCV edge detection and matrix solver into WebAssembly (Wasm) for client-side zero-latency offline operation.
3. **Local Tesseract OCR Ingestion:** Embedding OCR text extraction to output searchable, selectable PDF documents directly.
4. **Multi-Page Batch Processing:** Implementing session persistence and automated PDF compilation for multi-page documents.

---

## 19. Conclusion

The Smart Document Scanner demonstrates the viability, speed, and precision of explainable classical Computer Vision for document perspective rectification. By combining Canny edge filtering, contour topological analysis, Douglas-Peucker simplification, and SVD-based planar homography, the system achieves sub-2-pixel localization accuracy with single-digit millisecond latency. The responsive web application and interactive SVG corner editor ensure practical utility even in challenging photographic conditions.

---

## 20. References

1. OpenCV Documentation. *Geometric Image Transformations: getPerspectiveTransform, warpPerspective.* https://docs.opencv.org/
2. Canny, J. *A Computational Approach to Edge Detection.* IEEE Transactions on Pattern Analysis and Machine Intelligence, 1986.
3. Suzuki, S., & Abe, K. *Topological structural analysis of digitized binary images by border following.* Computer Vision, Graphics, and Image Processing, 1985.
4. Hartley, R., & Zisserman, A. *Multiple View Geometry in Computer Vision.* Cambridge University Press, 2nd Edition.
5. FastAPI Documentation. *FastAPI Framework, High Performance Web APIs.* https://fastapi.tiangolo.com/
6. React Documentation. *Managing State, Event Handling, and Hooks.* https://react.dev/
