# SmartScan: Smart Document Scanner

An educational and production-ready Image Processing and Computer Vision (IPCV) web application that detects document boundaries in arbitrary photographs, applies planar homography for perspective rectification, and enhances readability using classical computer vision algorithms.

---

## Features

- **Automated Document Detection:** Multi-stage edge detection (Canny, Otsu, and Adaptive Thresholding) with Suzuki contour extraction and Douglas-Peucker polygon approximation.
- **Robust Corner Ordering:** Deterministic clockwise sorting (`Top-Left`, `Top-Right`, `Bottom-Right`, `Bottom-Left`) with winding consistency and geometric validation.
- **Perspective Rectification:** 8-DOF planar homography transformation via Direct Linear Transformation (DLT) and bicubic backward warping.
- **Interactive SVG Corner Editor:** Draggable corner handles and a 4-point click-to-place fallback mode when automatic detection encounters low-contrast backgrounds.
- **Multi-Mode Enhancement Filters:**
  - **Color:** Preserves natural colors in the perspective-straightened image.
  - **Grayscale:** Standard luminance extraction ($Y = 0.299R + 0.587G + 0.114B$).
  - **Black & White:** Adaptive Gaussian thresholding ($21 \times 21$ window) for sharp, high-contrast text scanning.
  - **Contrast:** CLAHE (Contrast Limited Adaptive Histogram Equalization) applied to the CIE-Lab $L^*$ luminance channel.
- **Interactive Comparison Workspace:** Side-by-side view and split-slider interactive comparison between distorted photo and rectified document.
- **Multi-Format Export:** Direct downloads for Original, Corrected PNG, Enhanced PNG, and formatted A4 PDF.
- **Quantitative Evaluation Framework:** Built-in benchmarking script calculating detection success rate, Euclidean corner error, normalized diagonal error, and latency against mathematically verified ground truth.

---

## Technology Stack

### Frontend
- **Framework:** React 18
- **Build Tool:** Vite 5
- **Styling:** Tailwind CSS 3
- **Icons:** Lucide React
- **Testing:** Vitest & React Testing Library

### Backend
- **Framework:** FastAPI 0.119
- **Server:** Uvicorn
- **Image Processing:** OpenCV 4.11 Headless & NumPy
- **Image I/O & EXIF:** Pillow 11
- **PDF Generation:** ReportLab 4.4
- **Testing:** Pytest & HTTPX TestClient

---

## Directory Structure

```
smart-document-scanner/
├── backend/
│   ├── app/
│   │   ├── services/
│   │   │   ├── image_validation.py      # EXIF normalization and image bounds checking
│   │   │   ├── preprocessing.py         # Dimension normalization and Canny/Otsu filters
│   │   │   ├── document_detection.py    # Contour ranking, Douglas-Peucker, and annotation
│   │   │   ├── perspective.py           # Corner ordering and homography warping
│   │   │   ├── enhancement.py           # Adaptive thresholding and CLAHE filters
│   │   │   ├── metrics.py               # Corner Euclidean and normalized error metrics
│   │   │   └── pdf_export.py            # A4 PDF document formatting and export
│   │   ├── config.py                    # Application parameters and limits
│   │   ├── schemas.py                   # Pydantic request and response schemas
│   │   └── main.py                      # FastAPI REST routes and exception handlers
│   ├── tests/                           # 19 automated backend test cases
│   ├── requirements.txt
│   └── pytest.ini
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── Header.jsx               # Branding, backend health pill, and modal triggers
│   │   │   ├── UploadPanel.jsx          # Drag-and-drop file upload with format check
│   │   │   ├── ImageWorkspace.jsx       # Multi-tab image canvas with SVG corner editor
│   │   │   ├── CornerEditor.jsx         # Interactive draggable handles and 4-point click mode
│   │   │   ├── ProcessingControls.jsx   # Detect, warp, enhancement pills, and smart scan
│   │   │   ├── ComparisonView.jsx       # Side-by-side and interactive split slider
│   │   │   ├── DownloadPanel.jsx        # PNG and PDF export triggers
│   │   │   ├── MetricsPanel.jsx         # Quantitative diagnostics and corner coordinates
│   │   │   └── InfoModal.jsx            # Educational guide explaining the 6 CV steps
│   │   ├── hooks/
│   │   │   └── useDocumentScanner.js    # State machine and guarded workflow transitions
│   │   ├── utils/
│   │   │   └── imageUtils.js            # Coordinate normalization and geometry checks
│   │   ├── services/
│   │   │   └── api.js                   # REST API client
│   │   └── App.jsx
│   ├── package.json
│   └── vite.config.js
├── dataset/
│   ├── sample_images/                   # 10 synthetic test cases with varied geometry
│   ├── ground_truth/                    # Ground truth corner JSON catalog
│   └── evaluation_results.csv           # Detailed benchmark export
├── docs/
│   ├── PROJECT_REPORT.md                # Formal 20-section college project report
│   ├── ALGORITHM_EXPLANATION.md         # Detailed mathematical formulas and derivations
│   ├── TESTING_REPORT.md                # Comprehensive verification and benchmark logs
│   ├── VIVA_QUESTIONS.md                # 30 oral exam questions with full answers
│   └── PRESENTATION_OUTLINE.md          # 12-slide college presentation outline
├── scripts/
│   ├── generate_test_dataset.py         # Synthetic document generation script
│   └── evaluate_dataset.py              # Quantitative evaluation and benchmark runner
├── LICENSE
└── README.md
```

---

## Installation & Setup

### Prerequisites
- **Python:** 3.10, 3.11, or 3.12 installed
- **Node.js:** v18+ or v20+ with npm

---

### Step 1: Backend Setup

#### On macOS & Linux:
```bash
cd smart-document-scanner
python3 -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt
```

#### On Windows (Command Prompt / PowerShell):
```cmd
cd smart-document-scanner
python -m venv .venv
.venv\Scripts\activate
pip install -r backend\requirements.txt
```

---

### Step 2: Frontend Setup

```bash
cd smart-document-scanner/frontend
npm install
```

---

## Running the Application

### 1. Start the Backend API Server

From the `smart-document-scanner` folder (with virtual environment activated):

```bash
cd backend
python -m uvicorn app.main:app --reload --port 8000
```
- The backend API will be available at: `http://localhost:8000`
- Interactive OpenAPI / Swagger documentation: `http://localhost:8000/docs`
- Health check: `http://localhost:8000/api/health`

### 2. Start the Frontend Development Server

In a second terminal, navigate to the frontend directory:

```bash
cd smart-document-scanner/frontend
npm run dev
```
- The web application will launch at: `http://localhost:3000` (or `http://localhost:5173`)

---

## Running Automated Tests

### Run Backend Tests (19 Tests)
```bash
cd smart-document-scanner/backend
source ../.venv/bin/activate    # or ..\.venv\Scripts\activate on Windows
PYTHONPATH=. pytest -v
```

### Run Frontend Tests (8 Tests)
```bash
cd smart-document-scanner/frontend
npm run test
```

### Run Quantitative Evaluation Benchmark
```bash
cd smart-document-scanner
source .venv/bin/activate       # or .venv\Scripts\activate on Windows
python scripts/evaluate_dataset.py
```

---

## Benchmark Results

Evaluated on 10 controlled scenarios (`scripts/evaluate_dataset.py`):

| Metric | Target Specification | Measured Result |
| :--- | :--- | :--- |
| **Detection Success Rate** | $\ge 90\%$ | **100.0%** (10 / 10) |
| **Mean Corner Error** | $\le 5.0$ px | **1.41 pixels** |
| **Normalized Corner Error** | $\le 0.5\%$ | **0.100%** |
| **Average Detection Latency** | $\le 50$ ms | **4.11 ms** per photo |

---

## REST API Documentation

| Method | Endpoint | Description | Payload |
| :--- | :--- | :--- | :--- |
| `GET` | `/api/health` | Service health status and OpenCV version | None |
| `POST` | `/api/detect` | Detects document boundary quadrilateral | Multipart image |
| `POST` | `/api/correct` | Warps perspective given 4 corner coordinates | Multipart image + corners JSON |
| `POST` | `/api/enhance` | Applies enhancement filter (`color`, `grayscale`, `black_white`, `contrast`) | Image data / file + mode |
| `POST` | `/api/process` | End-to-end detect, correct, and enhance pipeline | Multipart image + options |
| `POST` | `/api/export/pdf` | Converts rectified document into downloadable A4 PDF | Rectified image data |

---

## Documentation Links

- **Formal Project Report:** [`docs/PROJECT_REPORT.md`](docs/PROJECT_REPORT.md)
- **Mathematical Algorithm Derivations:** [`docs/ALGORITHM_EXPLANATION.md`](docs/ALGORITHM_EXPLANATION.md)
- **Software Testing & Verification Report:** [`docs/TESTING_REPORT.md`](docs/TESTING_REPORT.md)
- **Oral Examination / Viva Q&A (30 Questions):** [`docs/VIVA_QUESTIONS.md`](docs/VIVA_QUESTIONS.md)
- **Presentation Outline (12 Slides):** [`docs/PRESENTATION_OUTLINE.md`](docs/PRESENTATION_OUTLINE.md)

---

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.
