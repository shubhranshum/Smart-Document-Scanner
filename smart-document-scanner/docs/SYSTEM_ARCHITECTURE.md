# Smart Document Scanner: System Architecture & Algorithmic Blueprint

> **Project Title:** Smart Document Scanner: Document Detection and Perspective Correction Using Image Processing  
> **Domain:** Image Processing & Computer Vision (IPCV), Full-Stack Systems Engineering  
> **Architecture Pattern:** Client-Server Monorepo (React SPA + FastAPI High-Performance Vision Engine)  
> **Authors:** College Capstone Project Team  

---

## Table of Contents

1. [Executive Overview & Philosophy](#1-executive-overview--philosophy)
2. [End-to-End System Architecture](#2-end-to-end-system-architecture)
   - [2.1 High-Level Architecture Diagram](#21-high-level-architecture-diagram)
   - [2.2 Client-Tier Architecture (React 18 + Vite)](#22-client-tier-architecture-react-18--vite)
   - [2.3 API Gateway & Communication Contract](#23-api-gateway--communication-contract)
   - [2.4 Vision Engine Service Decomposition](#24-vision-engine-service-decomposition)
   - [2.5 Complete End-to-End Execution Sequence](#25-complete-end-to-end-execution-sequence)
3. [Exhaustive Algorithmic Breakdown](#3-exhaustive-algorithmic-breakdown)
   - [Algorithm 1: Aspect-Preserving Downsampling & Invariant Coordinate Mapping](#algorithm-1-aspect-preserving-downsampling--invariant-coordinate-mapping)
   - [Algorithm 2: Luminance & Chroma Space Transformation (BT.601 & HSV)](#algorithm-2-luminance--chroma-space-transformation-bt601--hsv)
   - [Algorithm 3: Spatial Filtering & Gaussian Kernel Smoothing](#algorithm-3-spatial-filtering--gaussian-kernel-smoothing)
   - [Algorithm 4: Mathematical Morphology for Non-Destructive Text Suppression](#algorithm-4-mathematical-morphology-for-non-destructive-text-suppression)
   - [Algorithm 5: Multi-Modal Document Segmentation Ensemble](#algorithm-5-multi-modal-document-segmentation-ensemble)
   - [Algorithm 6: Topological Border Following (Suzuki-Abe Algorithm)](#algorithm-6-topological-border-following-suzuki-abe-algorithm)
   - [Algorithm 7: Polygonal Simplification (Douglas-Peucker Algorithm)](#algorithm-7-polygonal-simplification-douglas-peucker-algorithm)
   - [Algorithm 8: Principal-Axis Rotated Extrema Quad Extraction](#algorithm-8-principal-axis-rotated-extrema-quad-extraction)
   - [Algorithm 9: Sub-Pixel Gradient Zero-Crossing Corner Refinement](#algorithm-9-sub-pixel-gradient-zero-crossing-corner-refinement)
   - [Algorithm 10: Multi-Criteria Physical Document Scoring Discriminator](#algorithm-10-multi-criteria-physical-document-scoring-discriminator)
   - [Algorithm 11: Deterministic Clockwise Corner Sorting & Winding Normalization](#algorithm-11-deterministic-clockwise-corner-sorting--winding-normalization)
   - [Algorithm 12: Planar Homography & Backward Bicubic Perspective Rectification](#algorithm-12-planar-homography--backward-bicubic-perspective-rectification)
   - [Algorithm 13: Document Readability Enhancement & Contrast Equalization](#algorithm-13-document-readability-enhancement--contrast-equalization)
   - [Algorithm 14: Vector PDF Generation & Physical Metric Scaling](#algorithm-14-vector-pdf-generation--physical-metric-scaling)
4. [Frontend Responsive Geometry & Interactive Vector Overlay](#4-frontend-responsive-geometry--interactive-vector-overlay)
5. [Error Handling, Boundary Guards, and Degradation Strategies](#5-error-handling-boundary-guards-and-degradation-strategies)
6. [Technology Stack & Dependency Matrix](#6-technology-stack--dependency-matrix)

---

## 1. Executive Overview & Philosophy

The **Smart Document Scanner** is an educational, production-ready computer vision application designed to digitize handheld photographs of documents captured at arbitrary angles and non-uniform lighting into straightened, high-readability, orthorectified scans.

```
       [Raw Angled Photo] ──► [Vision Engine] ──► [Orthorectified Document Scan]
             (Skewed, Shadowed)      (Explainable CV)         (Straightened, Clean B&W/Color)
```

### 1.1 Core Engineering Principles

1. **100% Explainable Classical Computer Vision:**  
   Unlike modern "black-box" deep learning models (e.g., YOLO or Mask-RCNN) which require gigabytes of neural weights, GPU acceleration, and lack deterministic explainability, this project relies purely on classical, mathematically rigorous Image Processing and Computer Vision (IPCV) techniques. Every single coordinate and pixel transformation can be traced back to differential geometry, linear algebra, and morphological set theory.
2. **Sub-100ms Latency on Standard CPU:**  
   All vision algorithms are optimized with aspect-preserving pyramid downsampling, spatial morphological kernels, and NumPy vectorized array operations, ensuring complete execution in under 70 ms on any commodity laptop CPU without requiring a GPU.
3. **Interactive Human-in-the-Loop Fallback:**  
   Computer vision edge detectors inherently face ambiguity in low-contrast environments (e.g., a white sheet on a white tablecloth). SmartScan bridges this gap through a high-precision, interactive SVG vector overlay that allows users to manually nudge corner handles or pick 4 points with real-time geometric validation.
4. **Resolution-Invariant Processing:**  
   Heavy differential operators run on a normalized detection scale to save CPU cycles and suppress microscopic paper fiber noise, but the final perspective transformation (homography warp) executes on the pristine, full-resolution source image (e.g., $12\text{ MP}$ phone photos).

---

## 2. End-to-End System Architecture

### 2.1 High-Level Architecture Diagram

```mermaid
flowchart TD
    subgraph ClientTier["Client Tier (Browser - React 18 SPA)"]
        UI["User Interface Components\n(Tailwind CSS + Lucide Icons)"]
        Hook["useDocumentScanner Hook\n(Client State Machine)"]
        SVG["Interactive SVG Vector Overlay\n(CornerEditor.jsx)"]
        Canvas["Comparison View / Canvas\n(Before / After Split Screen)"]
        UI --> Hook
        Hook --> SVG
        Hook --> Canvas
    end

    subgraph NetworkTier["Communication Layer"]
        HTTP["Asynchronous REST API (JSON / Multipart-FormData)"]
    end

    subgraph ServerTier["Server Tier (FastAPI Engine @ Python 3.12)"]
        Router["FastAPI Application Router\n(app/main.py)"]
        Val["Validation & EXIF Normalizer\n(app/services/image_validation.py)"]
        Pre["Aspect-Preserving Downsampler\n(app/services/preprocessing.py)"]
        Det["Multi-Modal Document Detection\n(app/services/document_detection.py)"]
        Persp["Homography & Perspective Warp\n(app/services/perspective.py)"]
        Enh["Readability Enhancement Engine\n(app/services/enhancement.py)"]
        PDF["Vector PDF Generation\n(app/services/pdf_export.py)"]

        Router --> Val
        Val --> Pre
        Pre --> Det
        Det --> Persp
        Persp --> Enh
        Enh --> PDF
    end

    ClientTier <==>|HTTP Requests / Base64 Data URLs| NetworkTier <==> ServerTier
```

---

### 2.2 Client-Tier Architecture (React 18 + Vite)

The frontend is constructed as a modern, reactive Single Page Application (SPA) designed with a clean, restrained light theme adhering to modern document-scanning UI paradigms.

```
frontend/src/
├── components/
│   ├── Header.jsx              # Application identity, title, status indicator
│   ├── UploadPanel.jsx         # Drag-and-drop zone with MIME and size filters
│   ├── ImageWorkspace.jsx      # Multi-tab unified viewport (Original, Detection, Corrected, Enhanced, Comparison)
│   ├── CornerEditor.jsx        # SVG responsive vector boundary with draggable handles & 4-point picker
│   ├── ProcessingControls.jsx  # Primary action buttons (Detect, Straighten, Enhance, Reset)
│   ├── ComparisonView.jsx      # Side-by-side and interactive split-slider comparison
│   ├── MetricsPanel.jsx        # Quantitative IPCV metrics (contour area, time, dimensions)
│   ├── DownloadPanel.jsx       # Format selector (PNG, JPEG, PDF) with instant export
│   └── InfoModal.jsx           # Educational explanation modal for demonstrations and viva
├── hooks/
│   └── useDocumentScanner.js   # Central state orchestrator & lifecycle manager
├── services/
│   └── api.js                  # Axios HTTP client with timeout and network fault tolerance
└── utils/
    └── imageUtils.js           # Client-side geometry validation & coordinate transforms
```

#### Frontend State Machine (`useDocumentScanner.js`)

```mermaid
stateDiagram-v2
    [*] --> Idle: Application Mount
    Idle --> Uploading: File Dragged / Selected
    Uploading --> Ready: Client Validation Passed
    Ready --> Detecting: Click "Detect Document"
    Detecting --> Detected: Backend Returns Corners
    Detecting --> ManualSelection: Detection Confidence Low
    Detected --> EditingCorners: Click "Adjust Corners"
    EditingCorners --> Detected: Save Corner Handles
    ManualSelection --> Detected: 4 Points Placed
    Detected --> Correcting: Click "Straighten Perspective"
    Correcting --> Corrected: Homography Warp Complete
    Corrected --> Enhancing: Select Filter Mode
    Enhancing --> Enhanced: Output Rendered
    Enhanced --> Exporting: Download Image / PDF
    Exporting --> [*]
```

---

### 2.3 API Gateway & Communication Contract

All communications between the browser client and the backend server are managed through RESTful endpoints defined with Pydantic schemas in [`backend/app/schemas.py`](file:///Users/shubhranshumishra/ipcv_project/smart-document-scanner/backend/app/schemas.py):

| HTTP Method | Route | Request Payload | Response Model | Description |
| :--- | :--- | :--- | :--- | :--- |
| `GET` | `/api/health` | None | `HealthResponse` | Verifies server uptime, OpenCV version, and API version. |
| `POST` | `/api/detect` | `multipart/form-data` (`file`) | `DetectionResponse` | Ingests raw photo; returns detected corners, metrics, and method tag. |
| `POST` | `/api/correct` | `file` + `corners` JSON string | `CorrectionResponse` | Warps quadrilateral region into a straightened rectangle. |
| `POST` | `/api/enhance` | `file` / `image_data` + `mode` | `EnhanceResponse` | Applies B&W adaptive, grayscale, or CLAHE filter. |
| `POST` | `/api/process` | `file` + `mode` + optional corners | `ProcessAllResponse` | Unified pipeline executing detect + correct + enhance in one pass. |
| `POST` | `/api/export/pdf`| `file` / `image_data` + `title` | `application/pdf` (binary stream) | Compiles rectified document into a standards-compliant PDF. |

---

### 2.4 Vision Engine Service Decomposition

The backend Python service is decoupled into isolated, single-responsibility modules:

```
backend/app/services/
├── image_validation.py    # Byte-stream decoding, MIME verification, EXIF orientation normalization
├── preprocessing.py       # Aspect-preserving downsampling, auto-Canny estimation, spatial blurring
├── document_detection.py  # Multi-modal segmentation, rotated extrema extraction, candidate scoring
├── perspective.py         # Quadrilateral geometry verification, corner ordering, homography matrix
├── enhancement.py         # Adaptive Gaussian thresholding, CLAHE luminance enhancement
├── pdf_export.py          # ReportLab PDF synthesis and vector embedding
└── metrics.py             # Quantitative evaluation (PSNR, SSIM, IoU, corner Euclidean error)
```

---

### 2.5 Complete End-to-End Execution Sequence

```mermaid
sequenceDiagram
    autonumber
    actor User as User (Browser)
    participant Client as React Client (Vite)
    participant API as FastAPI Router
    participant Engine as Vision Processing Engine

    User->>Client: Drag & drop photo (e.g., 4032x3024 JPEG)
    Client->>Client: Extract client dimensions & create blob URL
    Client->>API: POST /api/detect (Multipart file)
    API->>Engine: validate_and_decode_image() [EXIF transpose]
    Engine->>Engine: resize_for_detection() [Downsample to max 900px]
    Engine->>Engine: Multi-Modal Segmentation (HSV, Closed Otsu, Adaptive, Canny)
    Engine->>Engine: Contour extraction & Rotated Extrema Quad calculation
    Engine->>Engine: Score candidates & scale corners back to 4032x3024
    Engine-->>API: Return [TL, TR, BR, BL] coordinates
    API-->>Client: JSON response (corners, time, method)
    Client->>User: Render SVG vector polygon over clean photograph

    opt Manual Adjustment
        User->>Client: Drag corner handle to fine-tune perimeter
        Client->>Client: Update SVG vector points & validate convexity
    end

    User->>Client: Click "Straighten Perspective"
    Client->>API: POST /api/correct (File + Corners JSON)
    API->>Engine: order_corners() & compute_perspective_transform_dimensions()
    Engine->>Engine: cv2.getPerspectiveTransform() [Homography Matrix H]
    Engine->>Engine: cv2.warpPerspective() [Bicubic backward mapping]
    Engine-->>API: Straightened RGB image
    API-->>Client: Base64 Data URL (Straightened image)
    Client->>User: Display straightened rectangular document

    User->>Client: Select "B&W Document" mode
    Client->>API: POST /api/enhance (mode="black_white")
    Engine->>Engine: cv2.adaptiveThreshold() [Gaussian local binarization]
    Engine-->>API: Enhanced scan image
    API-->>Client: Base64 Data URL (Clean scan)
    Client->>User: Instant high-contrast document display
```

---

## 3. Exhaustive Algorithmic Breakdown

---

### Algorithm 1: Aspect-Preserving Downsampling & Invariant Coordinate Mapping

#### Intuition & Analogy
Imagine inspecting a large poster. Standing with your nose against the paper reveals tiny imperfections, paper fibers, and microscopic dots that distract you from seeing the poster's four edges. Stepping back 5 feet gives you a clear view of the poster's shape.  
Similarly, running edge detection on a huge 12-megapixel phone camera photo makes the computer detect every single paper grain, ink dot, and dust speck, while taking over 500 ms. Stepping back (downsampling to 900 px) removes high-frequency noise, speeds up computation by **$10\times$**, and reveals the true document boundary.

#### Mathematical Formulation
Given an input image $I \in \mathbb{R}^{H_{\text{orig}} \times W_{\text{orig}} \times 3}$ and a target maximum dimension $D_{\text{target}} = 900$:

$$\text{scale} = \begin{cases} 1.0 & \text{if } \max(H_{\text{orig}}, W_{\text{orig}}) \le D_{\text{target}} \\ \frac{D_{\text{target}}}{\max(H_{\text{orig}}, W_{\text{orig}})} & \text{otherwise} \end{cases}$$

The downsampled dimensions are:
$$W_{\text{res}} = \text{round}(W_{\text{orig}} \cdot \text{scale}), \quad H_{\text{res}} = \text{round}(H_{\text{orig}} \cdot \text{scale})$$

We compute the exact scale factors:
$$s_x = \frac{W_{\text{res}}}{W_{\text{orig}}}, \quad s_y = \frac{H_{\text{res}}}{H_{\text{orig}}}$$

Once the 4 corners $(x_i^{\text{res}}, y_i^{\text{res}})$ are detected on the downsampled image, they are mapped back to the original full-resolution coordinates with zero loss of precision:

$$x_i^{\text{orig}} = \text{clip}\left(\frac{x_i^{\text{res}}}{s_x}, 0, W_{\text{orig}} - 1\right), \quad y_i^{\text{orig}} = \text{clip}\left(\frac{y_i^{\text{res}}}{s_y}, 0, H_{\text{orig}} - 1\right)$$

#### Project Implementation Link
Implemented in [`backend/app/services/preprocessing.py`](file:///Users/shubhranshumishra/ipcv_project/smart-document-scanner/backend/app/services/preprocessing.py#L6-L30).

---

### Algorithm 2: Luminance & Chroma Space Transformation (BT.601 & HSV)

#### Intuition & Analogy
Colors can be deceptive. A blue ink stamp, a red company logo, or black text can confuse an edge detector into thinking there are boundaries all over the page. To find the paper's edge, we convert color into pure brightness (grayscale).  
Furthermore, human eyes perceive green light much more vividly than blue light. Grayscale conversion uses physiological weights to match human perception. Additionally, we convert to HSV (Hue, Saturation, Value) because white paper has almost **zero color saturation**, while wooden desks, floors, and bedsheets have **high color saturation**.

#### Mathematical Formulation

**1. Grayscale Conversion (ITU-R Recommendation BT.601):**
$$Y(x, y) = 0.299 \cdot R(x, y) + 0.587 \cdot G(x, y) + 0.114 \cdot B(x, y)$$

**2. HSV Color Space Conversion:**
Let $R', G', B' = \frac{R}{255}, \frac{G}{255}, \frac{B}{255}$.  
Let $C_{\max} = \max(R', G', B')$ and $C_{\min} = \min(R', G', B')$, with difference $\Delta = C_{\max} - C_{\min}$.

$$\text{Value } V = C_{\max}$$

$$\text{Saturation } S = \begin{cases} 0 & \text{if } C_{\max} = 0 \\ \frac{\Delta}{C_{\max}} & \text{if } C_{\max} \ne 0 \end{cases}$$

$$\text{Hue } H = \begin{cases} 0^\circ & \Delta = 0 \\ 60^\circ \times \left(\frac{G' - B'}{\Delta} \bmod 6\right) & C_{\max} = R' \\ 60^\circ \times \left(\frac{B' - R'}{\Delta} + 2\right) & C_{\max} = G' \\ 60^\circ \times \left(\frac{R' - G'}{\Delta} + 4\right) & C_{\max} = B' \end{cases}$$

#### Why It Matters in SmartScan
White and off-white paper consistently exhibits $S < 0.33$ ($S < 85$ on a 0–255 scale) and $V > 0.37$ ($V > 95$). Wooden tables, laminate desks, skin, and carpets have $S > 120$. This provides a clean separation boundary between paper and background.

---

### Algorithm 3: Spatial Filtering & Gaussian Kernel Smoothing

#### Intuition & Analogy
If you look closely at paper under a magnifying glass, it is rough and bumpy. Camera sensors also introduce electrical noise (graininess), especially in indoor lighting. Gaussian smoothing acts like a gentle digital defocuser: it blurs out high-frequency sensor noise while keeping structural edges intact.

#### Mathematical Formulation
A 2D continuous isotropic Gaussian function is defined as:

$$G(x, y; \sigma) = \frac{1}{2\pi \sigma^2} \exp\left(-\frac{x^2 + y^2}{2\sigma^2}\right)$$

In SmartScan, an odd-sized discrete kernel ($5 \times 5$, $\sigma \approx 1.4$) is generated:

$$K = \frac{1}{256} \begin{bmatrix} 1 & 4 & 6 & 4 & 1 \\ 4 & 16 & 24 & 16 & 4 \\ 6 & 24 & 36 & 24 & 6 \\ 4 & 16 & 24 & 16 & 4 \\ 1 & 4 & 6 & 4 & 1 \end{bmatrix}$$

The smoothed image is computed via 2D spatial convolution:

$$I_{\text{smooth}}(x, y) = (I * K)(x, y) = \sum_{i=-2}^{2} \sum_{j=-2}^{2} I(x - i, y - j) \cdot K(i + 2, j + 2)$$

---

### Algorithm 4: Mathematical Morphology for Non-Destructive Text Suppression

#### Intuition & Analogy
This is one of the project's critical breakthroughs.  
If you blur an image enough to make text disappear, you also turn the sharp edge of the paper into a fuzzy gradient, making precise corner detection impossible.  
**Morphological Closing** provides a solution: imagine rolling a flat $17 \times 17$ pixel square across the paper. The narrow, dark text letters ($< 8$ pixels wide) are completely filled in by surrounding white paper, while the large, straight outer boundary of the paper remains razor-sharp.

```
Raw Grayscale with Text           After 17x17 Morphological Closing
┌───────────────────────────┐    ┌───────────────────────────┐
│ White Paper Sheet         │    │ White Paper Sheet         │
│  "Lorem ipsum dolor sit"  │───►│  (Solid white continuous) │
│  "consectetur adipiscing" │    │  (Zero internal holes)    │
│  "sed do eiusmod tempor"  │    │  (Sharp outer perimeter)  │
└───────────────────────────┘    └───────────────────────────┘
```

#### Mathematical Formulation
Mathematical morphology operates on set theory over Euclidean spaces. Let $f(x, y)$ denote the grayscale image and $B$ denote a flat structuring element (a $17 \times 17$ rectangular kernel):

**1. Dilation ($\oplus$):** Expands bright regions (replaces each pixel with the neighborhood maximum):
$$(f \oplus B)(x, y) = \sup_{(i, j) \in B} f(x - i, y - j)$$

**2. Erosion ($\ominus$):** Shrinks bright regions (replaces each pixel with the neighborhood minimum):
$$(f \ominus B)(x, y) = \inf_{(i, j) \in B} f(x + i, y + j)$$

**3. Morphological Closing ($\bullet$):** Dilation followed by erosion:
$$f \bullet B = (f \oplus B) \ominus B$$

Because dark text consists of narrow local minima, dilation fills the text with surrounding bright paper values. The subsequent erosion restores the outer paper boundary to its exact original dimensions without reopening the filled text holes.

#### Project Implementation Link
Implemented in [`backend/app/services/document_detection.py`](file:///Users/shubhranshumishra/ipcv_project/smart-document-scanner/backend/app/services/document_detection.py#L295-L330).

---

### Algorithm 5: Multi-Modal Document Segmentation Ensemble

#### Intuition & Analogy
In the real world, no single thresholding strategy works everywhere. A white sheet on a brown wooden desk is easy for color thresholding. But white paper on a white tablecloth fails color thresholding and requires gradient edges. A document under a lamp has a bright side and a dark shadow side, causing global thresholding (Otsu) to slice the paper in half.  
SmartScan addresses this with an **ensemble of 6 distinct segmentation modalities**, running simultaneously and nominating candidates for ranking:

```mermaid
flowchart LR
    Img["Input Image"] --> M1["Modality 1: HSV Paper Mask"]
    Img --> M2["Modality 2: Text-Erased Otsu (Direct & Inverted)"]
    Img --> M3["Modality 3: Adaptive Gaussian (Shadow-Resilient)"]
    Img --> M4["Modality 4: Multi-Channel Color Canny"]
    Img --> M5["Modality 5: Standard Luminance Auto-Canny"]
    Img --> M6["Modality 6: CLAHE Local Contrast Canny"]

    M1 & M2 & M3 & M4 & M5 & M6 --> Merge["Candidate Extraction & Universal Scoring"]
```

#### Detailed Breakdown of Modalities

1. **HSV Chroma/Luma Paper Masking:**
   $$\text{Mask}_{\text{HSV}}(x, y) = [S(x, y) < 85] \land [V(x, y) > 95]$$
   Isolates desaturated, high-reflectance paper from wood, fabric, and skin.

2. **Text-Erased Bimodal Otsu Segmentation (Direct & Inverted):**
   Calculates global threshold $T^*$ by maximizing between-class variance $\sigma_B^2(T)$:
   $$\sigma_B^2(T) = \omega_0(T) \omega_1(T) \left[\mu_0(T) - \mu_1(T)\right]^2$$
   Where $\omega_0, \omega_1$ are class probabilities and $\mu_0, \mu_1$ are class means.  
   Both direct ($\text{paper} = 255$) and inverse ($\text{paper} = 0$, inverted via bitwise NOT) are extracted, supporting dark-mode certificates or chalkboards.

3. **Adaptive Gaussian Luminance Segmentation:**
   Calculates dynamic threshold $T(x, y)$ for each pixel based on a local $51 \times 51$ neighborhood weighted by a Gaussian window minus constant $C = 8$:
   $$T(x, y) = \left( \sum_{i=-25}^{25} \sum_{j=-25}^{25} G(i, j) \cdot I(x+i, y+j) \right) - 8$$
   This resolves non-uniform lighting and strong diagonal smartphone shadows.

4. **Multi-Channel Color Canny Edge Detection:**
   Calculates horizontal and vertical Sobel gradients across all three channels ($R, G, B$) and computes the maximum gradient response at each coordinate:
   $$E_{\text{color}}(x, y) = \max\left( E_R(x, y), E_G(x, y), E_B(x, y) \right)$$
   A $9 \times 9$ morphological closing is applied to seal small perimeter breaks caused by edge highlights.

---

### Algorithm 6: Topological Border Following (Suzuki-Abe Algorithm)

#### Intuition & Analogy
Once we have a black-and-white mask showing where the paper is, we need to trace its outline.  
`cv2.findContours` implements the classical **Suzuki-Abe algorithm**, which moves along boundary pixels like a pen tracing around a shape.  
Importantly, we use `cv2.RETR_LIST` rather than `cv2.RETR_EXTERNAL`. If a document is resting on a desk in a room, the room's floor is the outermost border, and the document is an *internal* shape. `RETR_LIST` ensures that nested shapes are fully captured.

#### Mathematical Formulation
The algorithm scans raster lines until it encounters a transition pixel:
* Transition from 0 to 1: Outer border.
* Transition from 1 to 0: Hole border.

It follows border pixels using 8-connectivity, recording sequential coordinates:
$$\mathcal{C} = \{ (x_0, y_0), (x_1, y_1), \dots, (x_{n-1}, y_{n-1}) \}$$

The enclosed area is computed using the discrete **Shoelace formula (Green's Theorem)**:

$$\text{Area}(\mathcal{C}) = \frac{1}{2} \left| \sum_{i=0}^{n-1} (x_i y_{i+1} - x_{i+1} y_i) \right|, \quad \text{with } (x_n, y_n) = (x_0, y_0)$$

The perimeter (arc length) is the sum of Euclidean segments:

$$\text{Perimeter}(\mathcal{C}) = \sum_{i=0}^{n-1} \sqrt{(x_{i+1} - x_i)^2 + (y_{i+1} - y_i)^2}$$

---

### Algorithm 7: Polygonal Simplification (Douglas-Peucker Algorithm)

#### Intuition & Analogy
A hand-traced document boundary contains 500 to 1,500 individual pixel points, with small wiggles along the edge. We want to reduce those hundreds of points down to the 4 corners of a clean quadrilateral.  
The **Douglas-Peucker algorithm** draws a straight line between the start and end of a curve, finds the point farthest from that line, and if that distance is greater than a threshold $\epsilon$, splits the curve there. It repeats this until all intermediate points lie within $\epsilon$ of the simplified shape.

```
       Curve Points                       Simplified (4 Vertices)
        *   *                                  TL ┌────────────┐ TR
      *       *      ───[Douglas-Peucker]───►     │            │
    *           *     (Tolerance ε = 0.02 * P)    │            │
  *               *                            BL └────────────┘ BR
```

#### Mathematical Formulation
Given curve points $P_1, P_2, \dots, P_n$:
1. Construct line $L$ connecting endpoint $P_1$ to $P_n$:
   $$A x + B y + C = 0$$
   Where $A = y_1 - y_n$, $B = x_n - x_1$, $C = x_1 y_n - x_n y_1$.
2. For each intermediate point $P_i = (x_i, y_i)$, compute perpendicular distance $d(P_i, L)$:
   $$d(P_i, L) = \frac{|A x_i + B y_i + C|}{\sqrt{A^2 + B^2}}$$
3. Find maximum distance: $d_{\max} = \max_{1 < i < n} d(P_i, L)$ at index $k$.
4. If $d_{\max} > \epsilon$:
   Recursively simplify sub-curves $\{P_1, \dots, P_k\}$ and $\{P_k, \dots, P_n\}$.
5. If $d_{\max} \le \epsilon$:
   Discard all intermediate points; approximate segment as chord $\overline{P_1 P_n}$.

SmartScan dynamically tests a spectrum of perimeter-proportional tolerances:
$$\epsilon \in \{0.015, 0.02, 0.025, 0.03, 0.04, 0.06, 0.08\} \cdot \text{Perimeter}$$

---

### Algorithm 8: Principal-Axis Rotated Extrema Quad Extraction

#### Intuition & Analogy
In real photos, paper corners are rarely sharp mathematical points. They may be slightly bent, folded, rounded by scissors, or clipped.  
When Douglas-Peucker runs on a rounded corner, it produces 2 points per corner, yielding a 5-, 6-, or 8-sided polygon instead of a 4-sided one.  
To address this, we compute the document's overall tilt angle ($\theta$), rotate the shape into a level, horizontal frame, and find the four extreme points: top-left, top-right, bottom-right, and bottom-left. Then we rotate those four points back. This extracts the **4 true geometric corners**, even if the physical corners are rounded.

```
 Rounded Corner Shape                   Aligned to Principal Axis θ
       ┌───────┐                                 (x-y min)   (x+y max)
     /           \                                  TL ┌───┐ TR
    │   Paper     │      ───[Rotate by -θ]───►         │   │
     \           /                                  BL └───┘ BR
       └───────┘                                 (x+y min)   (x-y max)
```

#### Mathematical Formulation
1. Given convex hull vertices $H \in \mathbb{R}^{N \times 2}$ ($N \ge 4$):
2. Compute the Minimum-Area Bounding Rectangle via rotating calipers (`cv2.minAreaRect`):
   $$\text{rect} = ( (c_x, c_y), (W_{\text{box}}, H_{\text{box}}), \theta )$$
3. Construct rotation matrix $\mathbf{R}_{-\theta}$ to align the shape:
   $$\mathbf{R}_{-\theta} = \begin{bmatrix} \cos(-\theta) & -\sin(-\theta) \\ \sin(-\theta) & \cos(-\theta) \end{bmatrix}$$
4. Project all hull vertices into the aligned canonical plane:
   $$\mathbf{p}_i^{\text{aligned}} = \mathbf{R}_{-\theta} \cdot \left( \mathbf{p}_i - \mathbf{c} \right)$$
5. In the canonical plane, the 4 corners correspond to the four diagonal extrema:
   $$s_i = x_i^{\text{aligned}} + y_i^{\text{aligned}}, \quad d_i = x_i^{\text{aligned}} - y_i^{\text{aligned}}$$
   $$\text{Index}_{\text{TL}} = \arg\min(s), \quad \text{Index}_{\text{BR}} = \arg\max(s)$$
   $$\text{Index}_{\text{TR}} = \arg\max(d), \quad \text{Index}_{\text{BL}} = \arg\min(d)$$
6. Select the original coordinates:
   $$Q = \{ H[\text{Index}_{\text{TL}}], H[\text{Index}_{\text{TR}}], H[\text{Index}_{\text{BR}}], H[\text{Index}_{\text{BL}}] \}$$

#### Project Implementation Link
Implemented in [`backend/app/services/document_detection.py`](file:///Users/shubhranshumishra/ipcv_project/smart-document-scanner/backend/app/services/document_detection.py#L27-L45).

---

### Algorithm 9: Sub-Pixel Gradient Zero-Crossing Corner Refinement

#### Intuition & Analogy
Pixels on a computer screen are small discrete squares. If a document corner falls in the middle of a pixel, rounding to the nearest whole integer introduces a small error.  
`cv2.cornerSubPix` provides sub-pixel refinement: it examines the gradient vectors around the estimated corner and finds the exact floating-point intersection where the two edge gradients meet.

#### Mathematical Formulation
At a true corner $q$, the vector from $q$ to any neighboring pixel $p$ is orthogonal to the image gradient $\nabla I(p)$ at $p$:

$$\nabla I(p)^T \cdot (q - p) = 0$$

Across all pixels $p_i$ in a local $5 \times 5$ neighborhood window:

$$\sum_{i} \nabla I(p_i) \nabla I(p_i)^T \cdot q = \sum_{i} \nabla I(p_i) \nabla I(p_i)^T \cdot p_i$$

Let $\mathbf{G} = \sum_{i} \begin{bmatrix} I_x^2(p_i) & I_x(p_i) I_y(p_i) \\ I_x(p_i) I_y(p_i) & I_y^2(p_i) \end{bmatrix}$ and $\mathbf{b} = \sum_{i} \begin{bmatrix} I_x^2(p_i) x_i + I_x(p_i) I_y(p_i) y_i \\ I_x(p_i) I_y(p_i) x_i + I_y^2(p_i) y_i \end{bmatrix}$.

The sub-pixel refined coordinate $q^*$ is solved directly:
$$q^* = \mathbf{G}^{-1} \mathbf{b}$$

#### Project Implementation Link
Implemented in [`backend/app/services/document_detection.py`](file:///Users/shubhranshumishra/ipcv_project/smart-document-scanner/backend/app/services/document_detection.py#L76-L88).

---

### Algorithm 10: Multi-Criteria Physical Document Scoring Discriminator

#### Intuition & Analogy
Suppose the detector finds three valid quadrilaterals:
1. The dark wooden table (area 70%).
2. The white sheet of paper on the table (area 30%).
3. A paragraph box of text printed inside the paper (area 10%).

A simple area-based detector will pick the table because it is the largest.  
Our scoring function checks for **physical document signatures**:
- Does it have white paper brightness? (Table fails).
- Does it contain printed text? (Table fails).
- Is it brighter than its background? (Table fails).
- Is it larger than an individual paragraph? (Paragraph box loses).

The true document wins consistently across all criteria.

#### Mathematical Formulation
Every candidate quadrilateral $Q$ is evaluated using a composite scoring function:

$$\text{Score}(Q) = 0.25 \cdot S_{\text{bright}} + 0.25 \cdot S_{\text{text}} + 0.20 \cdot S_{\text{contrast}} + 0.15 \cdot S_{\text{edge}} + 0.10 \cdot S_{\text{parallel}} + 0.05 \cdot S_{\text{aspect}}$$

Where:

1. **Paper Brightness ($S_{\text{bright}}$):**
   $$S_{\text{bright}} = \text{clip}\left(\frac{\mu_{\text{inside}} - 100.0}{130.0}, 0.0, 1.0\right)$$
   *Penalty:* If $\mu_{\text{inside}} < 95.0$, $S_{\text{bright}} \leftarrow S_{\text{bright}} \times 0.15$ (disqualifies dark wooden tables, floor tiles, and black mousepads).

2. **Text / Content Entropy ($S_{\text{text}}$):**
   Computed via the standard deviation of the discrete Laplacian operator:
   $$\Delta I(x, y) = \frac{\partial^2 I}{\partial x^2} + \frac{\partial^2 I}{\partial y^2}$$
   $$S_{\text{text}} = \min\left(1.0, \frac{\sigma\left(\Delta I_{\text{inside}}\right)}{22.0}\right)$$
   Text characters produce high-frequency Laplacian variance ($\sigma > 50$), while blank desks and mousepads have $\sigma < 8$.

3. **Signed Contrast with Background ($S_{\text{contrast}}$):**
   $$S_{\text{contrast}} = \text{clip}\left(\frac{\mu_{\text{inside}} - \mu_{\text{outside}} + 20.0}{90.0}, 0.0, 1.0\right)$$
   Reflects that document paper is brighter than the supporting surface.

4. **Physical Gradient Coincidence ($S_{\text{edge}}$):**
   Measures the fraction of the candidate's perimeter mask $M_{\text{edge}}$ that aligns with peaks in the Canny edge map $E$:
   $$S_{\text{edge}} = \min\left(1.0, \frac{\sum (M_{\text{edge}} \land E)}{\sum M_{\text{edge}}} \times 5.0\right)$$

5. **Perspective Edge Parallelism ($S_{\text{parallel}}$):**
   Given edge lengths $w_1 = \|p_1 - p_0\|$, $w_2 = \|p_2 - p_3\|$, $h_1 = \|p_3 - p_0\|$, $h_2 = \|p_2 - p_1\|$:
   $$S_{\text{parallel}} = \frac{1}{2} \left( \frac{\min(w_1, w_2)}{\max(w_1, w_2)} + \frac{\min(h_1, h_2)}{\max(h_1, h_2)} \right)$$

6. **Camera Viewport Disqualification:**
   If $\frac{\text{Area}(Q)}{\text{Area}_{\text{total}}} > 0.94$, then $\text{Score}(Q) \leftarrow \text{Score}(Q) \times 0.05$.

#### Project Implementation Link
Implemented in [`backend/app/services/document_detection.py`](file:///Users/shubhranshumishra/ipcv_project/smart-document-scanner/backend/app/services/document_detection.py#L90-L190).

---

### Algorithm 11: Deterministic Clockwise Corner Sorting & Winding Normalization

#### Intuition & Analogy
Before applying perspective correction, the computer needs to know which corner is which:
Which is Top-Left? Top-Right? Bottom-Right? Bottom-Left?  
If corners are mixed up (e.g., passing Top-Left as Bottom-Right), the perspective transform will flip or twist the document inside out.  
We calculate the shape's center of mass (centroid), measure the angle from the center to each corner, arrange them clockwise, and assign index 0 to the corner closest to the origin $(0, 0)$.

```
   Centroid Angular Sort                   Clockwise Normalization
           y                                    p0(TL) ─────── p1(TR)
           │                                       │             │
      p3   │   p0                                  │   Document  │
   ────────┼────────► x                            │             │
      p2   │   p1                               p3(BL) ─────── p2(BR)
```

#### Mathematical Formulation
1. Given 4 points $\{p_0, p_1, p_2, p_3\}$:
2. Compute centroid coordinates $(\bar{x}, \bar{y})$:
   $$\bar{x} = \frac{1}{4} \sum_{i=0}^3 x_i, \quad \bar{y} = \frac{1}{4} \sum_{i=0}^3 y_i$$
3. Compute polar angle relative to centroid:
   $$\theta_i = \text{atan2}(y_i - \bar{y}, x_i - \bar{x}) \in (-\pi, \pi]$$
4. Sort points in ascending order of $\theta_i$.
5. Verify clockwise winding direction via vector cross product of consecutive edges:
   $$\mathbf{v}_1 = p_1 - p_0, \quad \mathbf{v}_2 = p_2 - p_1$$
   $$\text{Cross}(\mathbf{v}_1, \mathbf{v}_2) = v_{1x} v_{2y} - v_{1y} v_{2x}$$
   If $\text{Cross} < 0$, reverse array order to ensure strict clockwise sequence.
6. Identify the Top-Left corner by minimizing the distance to the coordinate origin $(0, 0)$:
   $$\text{TL\_index} = \arg\min_{i} (x_i + y_i)$$
7. Circularly roll array so index 0 is Top-Left:
   $$P_{\text{ordered}} = [p_{\text{TL}}, p_{\text{TR}}, p_{\text{BR}}, p_{\text{BL}}]$$

#### Project Implementation Link
Implemented in [`backend/app/services/perspective.py`](file:///Users/shubhranshumishra/ipcv_project/smart-document-scanner/backend/app/services/perspective.py#L60-L113).

---

### Algorithm 12: Planar Homography & Backward Bicubic Perspective Rectification

#### Intuition & Analogy
When you photograph a document from an angle, the side closer to the camera looks larger, and parallel lines converge toward a vanishing point (perspective distortion).  
A **Planar Homography** is a $3 \times 3$ transformation matrix that maps coordinates between two planes. We calculate the homography that maps the distorted quadrilateral into an upright rectangle, straightening the document.  
We use **backward mapping**: for every pixel in the clean output image, we calculate its source location in the original image using bicubic interpolation. This avoids gaps or holes in the output.

```
 Angled Quadrilateral (Source)               Rectified Output (Destination)
        (x0,y0) ─────── (x1,y1)                      (0,0) ─────────── (W,0)
           \               /                           │                 │
            \   Planar    /      ───[H Matrix]───►     │    Straight     │
             \ Homography/                             │    Document     │
              \         /                              │                 │
           (x3,y3) ─── (x2,y2)                       (0,H) ─────────── (W,H)
```

#### Mathematical Formulation

**1. Output Dimensions Estimation:**
The destination width $W_{\text{dst}}$ and height $H_{\text{dst}}$ are determined by the maximum Euclidean lengths of opposing edges:

$$W_{\text{top}} = \sqrt{(x_1 - x_0)^2 + (y_1 - y_0)^2}, \quad W_{\text{bottom}} = \sqrt{(x_2 - x_3)^2 + (y_2 - y_3)^2}$$
$$H_{\text{left}} = \sqrt{(x_3 - x_0)^2 + (y_3 - y_0)^2}, \quad H_{\text{right}} = \sqrt{(x_2 - x_1)^2 + (y_2 - y_1)^2}$$
$$W_{\text{dst}} = \text{round}\left(\max(W_{\text{top}}, W_{\text{bottom}})\right), \quad H_{\text{dst}} = \text{round}\left(\max(H_{\text{left}}, H_{\text{right}})\right)$$

The four destination coordinates are:
$$p_0' = (0, 0), \quad p_1' = (W_{\text{dst}}-1, 0), \quad p_2' = (W_{\text{dst}}-1, H_{\text{dst}}-1), \quad p_3' = (0, H_{\text{dst}}-1)$$

**2. Direct Linear Transformation (DLT) & SVD:**
Projective transformation in homogeneous coordinates is expressed as:
$$\begin{bmatrix} x' \\ y' \\ 1 \end{bmatrix} \sim \mathbf{H} \begin{bmatrix} x \\ y \\ 1 \end{bmatrix} = \begin{bmatrix} h_{11} & h_{12} & h_{13} \\ h_{21} & h_{22} & h_{23} \\ h_{31} & h_{32} & h_{33} \end{bmatrix} \begin{bmatrix} x \\ y \\ 1 \end{bmatrix}$$

Expanding into inhomogeneous equations:
$$x' = \frac{h_{11} x + h_{12} y + h_{13}}{h_{31} x + h_{32} y + h_{33}}, \quad y' = \frac{h_{21} x + h_{22} y + h_{23}}{h_{31} x + h_{32} y + h_{33}}$$

For each pair of corresponding points $(p_i, p_i')$, we obtain 2 linearly independent constraints, yielding an $8 \times 9$ system $\mathbf{A} \mathbf{h} = \mathbf{0}$:
$$\begin{bmatrix}
-x_i & -y_i & -1 & 0 & 0 & 0 & x_i' x_i & x_i' y_i & x_i' \\
0 & 0 & 0 & -x_i & -y_i & -1 & y_i' x_i & y_i' y_i & y_i'
\end{bmatrix} \begin{bmatrix} h_{11} \\ \vdots \\ h_{33} \end{bmatrix} = \mathbf{0}$$

We compute the Singular Value Decomposition (SVD):
$$\mathbf{A} = \mathbf{U} \mathbf{\Sigma} \mathbf{V}^T$$
The solution vector $\mathbf{h}$ is the singular vector corresponding to the smallest singular value (the last column of $\mathbf{V}$).

**3. Backward Bicubic Interpolation:**
To prevent holes, we use backward mapping: for every pixel $(u, v)$ in the output image, we map to $(x, y)$ in the source image via $\mathbf{H}^{-1}$:
$$\begin{bmatrix} x_s \\ y_s \\ w_s \end{bmatrix} = \mathbf{H}^{-1} \begin{bmatrix} u \\ v \\ 1 \end{bmatrix}, \quad x = \frac{x_s}{w_s}, \quad y = \frac{y_s}{w_s}$$

The pixel intensity is interpolated using a 2D Bicubic spline over a $4 \times 4$ neighborhood:
$$I(x, y) = \sum_{i=-1}^{2} \sum_{j=-1}^{2} I(\lfloor x \rfloor + i, \lfloor y \rfloor + j) \cdot W_{\text{cubic}}(x - (\lfloor x \rfloor + i)) \cdot W_{\text{cubic}}(y - (\lfloor y \rfloor + j))$$

#### Project Implementation Link
Implemented in [`backend/app/services/perspective.py`](file:///Users/shubhranshumishra/ipcv_project/smart-document-scanner/backend/app/services/perspective.py#L115-L196).

---

### Algorithm 13: Document Readability Enhancement & Contrast Equalization

#### Intuition & Analogy
A straightened document may still have shadows, a yellowish tint, or low contrast.  
SmartScan offers multiple enhancement modes:
- **Black & White Scan:** Uses local adaptive thresholding to turn paper pure white and text crisp black, like an office photocopy.
- **Grayscale:** Removes distracting color artifacts while preserving tonal gradations.
- **Contrast Boost (CLAHE):** Brightens shadowed corners without over-exposing already bright areas.

#### Mathematical Formulation

**1. Photocopy B&W Scan (Adaptive Gaussian Thresholding):**
$$I_{\text{out}}(x, y) = \begin{cases} 255 & \text{if } I_{\text{gray}}(x, y) \ge \left(\sum_{i=-10}^{10} \sum_{j=-10}^{10} G(i, j) \cdot I_{\text{gray}}(x+i, y+j)\right) - 10 \\ 0 & \text{otherwise} \end{cases}$$

**2. Contrast-Limited Adaptive Histogram Equalization (CLAHE):**
Standard histogram equalization stretches contrast across the entire image, which amplifies background noise in uniform paper areas.  
CLAHE divides the image into an $8 \times 8$ grid of contextual tiles, limits histogram amplification via a clip limit $\beta = 2.0$, redistributes clipped counts uniformly, and blends tiles using bilinear interpolation:

$$\beta = \text{ClipLimit} \cdot \left(\frac{N_{\text{pixels\_in\_tile}}}{N_{\text{bins}}}\right)$$

$$\text{Intensity } I_{\text{eq}}(x, y) = \text{BilinearInterpolate}\left( \text{CDF}_{\text{tile\_TL}}, \text{CDF}_{\text{tile\_TR}}, \text{CDF}_{\text{tile\_BL}}, \text{CDF}_{\text{tile\_BR}} \right)$$

#### Project Implementation Link
Implemented in [`backend/app/services/enhancement.py`](file:///Users/shubhranshumishra/ipcv_project/smart-document-scanner/backend/app/services/enhancement.py#L10-L75).

---

### Algorithm 14: Vector PDF Generation & Physical Metric Scaling

#### Intuition & Analogy
When creating a PDF, you shouldn't just paste an image into a file; it should match standard paper dimensions (A4, US Letter) with correct print resolution (72 DPI point scaling).  
The PDF engine calculates the aspect ratio of the rectified image and scales it into a standard A4 page ($595.27 \times 841.89$ points) with uniform margins.

#### Mathematical Formulation
Standard A4 dimensions in typographic points ($1\text{ pt} = \frac{1}{72}\text{ inch}$):
$$W_{\text{page}} = 595.27\text{ pt}, \quad H_{\text{page}} = 841.89\text{ pt}$$

Given margins $M = 36\text{ pt}$ ($0.5\text{ inch}$):
$$W_{\text{avail}} = W_{\text{page}} - 2M = 523.27\text{ pt}, \quad H_{\text{avail}} = H_{\text{page}} - 2M = 769.89\text{ pt}$$

Scale factor preserving aspect ratio:
$$s_{\text{pdf}} = \min\left( \frac{W_{\text{avail}}}{W_{\text{img}}}, \frac{H_{\text{avail}}}{H_{\text{img}}} \right)$$
$$W_{\text{render}} = W_{\text{img}} \cdot s_{\text{pdf}}, \quad H_{\text{render}} = H_{\text{img}} \cdot s_{\text{pdf}}$$

Centered placement offsets:
$$X_{\text{offset}} = M + \frac{W_{\text{avail}} - W_{\text{render}}}{2}, \quad Y_{\text{offset}} = M + \frac{H_{\text{avail}} - H_{\text{render}}}{2}$$

#### Project Implementation Link
Implemented in [`backend/app/services/pdf_export.py`](file:///Users/shubhranshumishra/ipcv_project/smart-document-scanner/backend/app/services/pdf_export.py#L15-L65).

---

## 4. Frontend Responsive Geometry & Interactive Vector Overlay

A common issue in web-based computer vision apps is alignment between browser screen coordinates and backend image pixels:

```
[Screen Display Space: 720 x 480 CSS px] ◄──► [Original Image Space: 4032 x 3024 Camera px]
```

### 4.1 Resolution-Independent Normalized SVG Coordinate Mapping

[`frontend/src/components/CornerEditor.jsx`](file:///Users/shubhranshumishra/ipcv_project/smart-document-scanner/frontend/src/components/CornerEditor.jsx) maps coordinates using an internal normalized SVG coordinate space of $1000 \times 1000$:

$$\text{svg}_X = \frac{x_{\text{orig}}}{W_{\text{orig}}} \times 1000, \quad \text{svg}_Y = \frac{y_{\text{orig}}}{H_{\text{orig}}} \times 1000$$

When the user drags a handle or clicks on the canvas, the mouse event $(e_{\text{clientX}}, e_{\text{clientY}})$ is converted back using the SVG bounding client rectangle:

$$\text{rel}_X = \text{clip}\left(\frac{e_{\text{clientX}} - \text{rect}_{\text{left}}}{\text{rect}_{\text{width}}}, 0.0, 1.0\right), \quad \text{rel}_Y = \text{clip}\left(\frac{e_{\text{clientY}} - \text{rect}_{\text{top}}}{\text{rect}_{\text{height}}}, 0.0, 1.0\right)$$

$$x_{\text{orig}}^{\text{new}} = \text{round}(\text{rel}_X \cdot W_{\text{orig}}), \quad y_{\text{orig}}^{\text{new}} = \text{round}(\text{rel}_Y \cdot H_{\text{orig}})$$

### 4.2 Ghost Boundary Elimination

Earlier iterations rendered a backend-annotated image with green lines burned into the pixel data, while simultaneously rendering interactive SVG vector lines on top. Any handle adjustment caused the two boundaries to diverge.  
The current architecture displays the pristine [`originalPreview`](file:///Users/shubhranshumishra/ipcv_project/smart-document-scanner/frontend/src/components/ImageWorkspace.jsx#L126) underneath, while [`CornerEditor.jsx`](file:///Users/shubhranshumishra/ipcv_project/smart-document-scanner/frontend/src/components/CornerEditor.jsx) renders the SVG vector polygon and draggable handles exclusively on top. This ensures **zero ghost lines** and consistent visual feedback during editing.

---

## 5. Error Handling, Boundary Guards, and Degradation Strategies

Robustness against invalid inputs is enforced across both client and server:

| Condition / Input | Failure Risk | Defense Mechanism | Response |
| :--- | :--- | :--- | :--- |
| **Non-Convex Polygon** | Tangled or folded homography warp | Evaluates edge vector cross-products: $\text{sign}(\mathbf{v}_i \times \mathbf{v}_{i+1}) = \text{constant}$ | `400 Bad Request` + Client UI alerts red dashed line |
| **Collinear Edges** | Rank-deficient matrix ($H$ cannot be inverted) | Triangle area checks between triples of points | Rejects selection, prompts handle adjustment |
| **Bowtie / Self-Intersecting** | Inverted or twisted perspective output | Vector segment intersection testing ($O(N^2)$ cross product check) | Rejects transformation, keeps user in editor |
| **Over-Sized Upload (> 15 MB)** | Server Out-of-Memory (OOM) | Strict stream byte count inspection before decoding | `413 Entity Too Large` with user guidance |
| **Corrupt / Non-Image File** | Decoder crash or buffer overflow | Pillow `verify()` check on raw byte stream | `400 Bad Request: Corrupted image stream` |
| **Low-Contrast / Cluttered Scene**| OpenCV misses 4-corner polygon | Fallback to rotated bounding box; if still invalid, triggers manual mode | `detected=False` + User prompted to pick 4 points |

---

## 6. Technology Stack & Dependency Matrix

```
Smart Document Scanner
├── Frontend (Client Tier)
│   ├── React 18.3.1           # Declarative component tree & virtual DOM
│   ├── Vite 5.4.21             # Build tool & Hot Module Replacement (HMR) dev server
│   ├── Tailwind CSS 3.4.17     # Utility-first responsive styling
│   ├── Lucide React 0.475.0    # Iconography system
│   └── Vitest 1.6.1            # Unit test runner
│
├── Backend (Vision Server Tier)
│   ├── Python 3.12.7           # Runtime environment
│   ├── FastAPI 0.115.11        # High-performance async ASGI web framework
│   ├── Uvicorn 0.34.0          # Production ASGI web server
│   ├── OpenCV 4.11.0 (headless)# Core Computer Vision & differential geometry algorithms
│   ├── NumPy 2.2.3             # Vectorized matrix operations & linear algebra (SVD)
│   ├── Pillow (PIL) 11.1.0     # Image ingestion & EXIF orientation normalization
│   ├── ReportLab 4.4.1         # Typographic vector PDF synthesis
│   └── Pytest 8.4.2            # Test automation & endpoint verification
```

---

## Summary for Viva & Mentors

When presenting this project to mentors or examiners, highlight these key design points:

1. **Why not use Deep Learning?**  
   Classical IPCV is lightweight, executes in **$50\text{ ms}$ on standard CPUs**, requires zero training data or GPUs, and every step is mathematically explainable.
2. **How does it distinguish documents from desks?**  
   It uses physical paper signatures: paper brightness ($\mu > 130$), Laplacian text entropy ($\sigma > 22$), signed contrast ($\text{paper} > \text{desk}$), and multi-channel color Canny edge coincidence.
3. **How does it resolve shadows and text?**  
   A $17 \times 17$ morphological closing suppresses narrow text lines without blurring outer paper edges, while adaptive Gaussian windowing normalizes illumination gradients.
4. **How does perspective correction work?**  
   It models the camera tilt as a **$3 \times 3$ Planar Homography matrix $\mathbf{H}$** solved via Direct Linear Transformation (SVD) and backward bicubic mapping.
