# Comprehensive Algorithm Explanation: Smart Document Scanner

This document provides a mathematical and algorithmic breakdown of the Computer Vision pipeline implemented in **SmartScan**.

---

## 1. Image Ingestion and Preprocessing

### 1.1 Grayscale Conversion
Color photographs contain three color channels: Red, Green, and Blue (RGB). Color variations across a document (ink color, logos) are secondary to structural boundary detection. The image is converted to a single intensity channel $Y$ using the ITU-R Recommendation BT.601 luminance weighting:

$$Y(x, y) = 0.299 \cdot R(x, y) + 0.587 \cdot G(x, y) + 0.114 \cdot B(x, y)$$

*Why these weights?* The human visual system has peak sensitivity to green wavelengths and lower sensitivity to blue.

```python
gray = cv2.cvtColor(image_rgb, cv2.COLOR_RGB2GRAY)
```

### 1.2 Gaussian Smoothing
Raw sensor data contains high-frequency thermal noise and fine texture. Convolving with a 2D Gaussian kernel suppresses noise while preserving dominant structural edges:

$$G(x, y; \sigma) = \frac{1}{2\pi \sigma^2} \exp\left(-\frac{x^2 + y^2}{2\sigma^2}\right)$$

In SmartScan, a $5 \times 5$ kernel with $\sigma \approx 1.4$ is applied:

$$I_{\text{smooth}} = I_{\text{gray}} * G_{5 \times 5}$$

```python
blurred = cv2.GaussianBlur(gray, (5, 5), 0)
```

---

## 2. Edge Detection via Canny Algorithm

The Canny operator is optimal according to three criteria: low error rate, localized edge points, and a single response to a single edge. It proceeds in four distinct steps:

### Step 2.1: Gradient Estimation
Spatial derivatives $I_x$ and $I_y$ are estimated using $3 \times 3$ Sobel convolution kernels:

$$K_x = \begin{bmatrix} -1 & 0 & 1 \\ -2 & 0 & 2 \\ -1 & 0 & 1 \end{bmatrix}, \quad K_y = \begin{bmatrix} -1 & -2 & -1 \\ 0 & 0 & 0 \\ 1 & 2 & 1 \end{bmatrix}$$

$$I_x = I_{\text{smooth}} * K_x, \quad I_y = I_{\text{smooth}} * K_y$$

The gradient magnitude $|G|$ and direction $\theta$ are:

$$|G(x, y)| = \sqrt{I_x^2(x, y) + I_y^2(x, y)}, \quad \theta(x, y) = \arctan\left(\frac{I_y(x, y)}{I_x(x, y)}\right)$$

### Step 2.2: Non-Maximum Suppression (NMS)
The edge gradient angle $\theta$ is rounded to one of four sectors: $0^\circ, 45^\circ, 90^\circ, 135^\circ$. A pixel is preserved if and only if its magnitude $|G|$ is strictly greater than both neighbors along the gradient normal vector. All other pixels are suppressed to 0.

### Step 2.3: Hysteresis Thresholding
Two thresholds $T_{\text{high}}$ and $T_{\text{low}}$ are computed adaptively based on the median intensity $v = \text{median}(I_{\text{smooth}})$:

$$T_{\text{low}} = \max(0, (1 - \sigma)v), \quad T_{\text{high}} = \min(255, (1 + \sigma)v), \quad \sigma = 0.33$$

1. If $|G| \ge T_{\text{high}}$, the pixel is marked as a **strong edge**.
2. If $T_{\text{low}} \le |G| < T_{\text{high}}$, the pixel is marked as a **weak edge**.
3. Weak edge pixels are retained only if connected to a strong edge in their 8-neighborhood.

```python
v = np.median(blurred)
lower = int(max(0, (1.0 - 0.33) * v))
upper = int(min(255, (1.0 + 0.33) * v))
edges = cv2.Canny(blurred, lower, upper)
```

### Step 2.4: Morphological Closing
Small gaps along the document perimeter caused by lighting irregularities are closed using morphological closing (dilation followed by erosion) with a $3 \times 3$ structuring element:

$$A \bullet B = (A \oplus B) \ominus B$$

```python
kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
edges_closed = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, kernel)
```

---

## 3. Multi-Strategy Segmentation & Candidate Extraction

Document boundaries in real environments encounter diverse lighting, textured surfaces (wood, granite, fabric), cast shadows, and internal text density. Relying on a single edge detection pass often fails. SmartScan deploys an ensemble of 5 complementary segmentation pipelines:

1. **Multi-Channel Color Canny:** Computes gradients across individual R, G, and B color channels:
   $$E_{\text{color}} = \max(E_R, E_G, E_B)$$
   Followed by morphological closing with a $(9 \times 9)$ structuring element to bridge broken perimeter segments.
2. **Macro Bimodal Otsu Segmentation:** Convolves grayscale intensity with a wide Gaussian kernel ($25 \times 25$) to blend away internal text lines, then applies Otsu thresholding to segment the solid paper blob. Both direct and inverse Otsu binarizations are evaluated.
3. **Adaptive Gaussian Luminance Segmentation:** Applies local window thresholding ($35 \times 35$) to isolate document edges under severe non-uniform lighting and phone shadows.
4. **CLAHE-Enhanced Luminance Canny:** Boosts local edge contrast in shadowed or underexposed corners.
5. **Standard Luminance Auto-Canny:** Fast baseline for high-contrast images.

### 3.1 4-Corner Extraction with Rotated Extrema
Real paper corners can be curled, folded, or rounded by camera lens distortion, causing Douglas-Peucker simplification to yield 5 to 16 vertices. SmartScan handles this robustly:
1. **Multi-Epsilon DP Sweep:** Tests $\epsilon \in [0.015, 0.10] \cdot P$ across candidate contours and convex hulls.
2. **Principal-Axis Rotated Extrema:** Computes the contour's minimum area bounding rectangle angle $\theta$, rotates hull vertices into the aligned canonical plane, and extracts the 4 extremal vertices minimizing/maximizing $(x \pm y)$.
3. **Combinatorial Area Maximization:** Evaluates convex hull vertex subsets to identify the 4-corner polygon that maximizes enclosed area.

### 3.2 Intelligent Document Candidate Scoring
Rather than blindly picking the largest contour (which often erroneously selects the desk or camera viewport) or the first contour, all candidates are ranked using a multi-criteria scoring function:

$$\text{Score} = 0.25 \cdot S_{\text{area}} + 0.25 \cdot S_{\text{contrast}} + 0.25 \cdot S_{\text{edge}} + 0.15 \cdot S_{\text{parallel}} + 0.10 \cdot S_{\text{aspect}}$$

Where:
- **$S_{\text{area}}$ (Area Priority):** Rewards documents in the realistic $20\% \le \text{area} \le 92\%$ frame ratio, while severely penalizing the camera frame ($>95\%$) and micro-noise ($<8\%$).
- **$S_{\text{contrast}}$ (Paper vs Background):** Evaluates $| \mu_{\text{inside}} - \mu_{\text{outside}} |$ to confirm the candidate bounds a distinct physical sheet.
- **$S_{\text{edge}}$ (Gradient Coincidence):** Measures the overlap between candidate perimeter edges and physical gradient peaks in the multi-channel Canny edge map.
- **$S_{\text{parallel}}$ (Edge Parallelism):** Checks that opposing edges obey realistic perspective convergence:
  $$S_{\text{parallel}} = \frac{1}{2} \left( \frac{\min(w_1, w_2)}{\max(w_1, w_2)} + \frac{\min(h_1, h_2)}{\max(h_1, h_2)} \right)$$
- **$S_{\text{aspect}}$ (Aspect Ratio Plausibility):** Verifies conformity to standard document aspect ratios ($0.35 \le w/h \le 3.2$).

---

## 4. Corner Ordering Algorithm

Given 4 unordered vertices $\{p_0, p_1, p_2, p_3\}$, we must deterministically identify:
- Index 0: Top-Left (TL)
- Index 1: Top-Right (TR)
- Index 2: Bottom-Right (BR)
- Index 3: Bottom-Left (BL)

### 4.1 Angular Centroid Sorting
1. Compute the centroid:
   $$\bar{x} = \frac{1}{4} \sum_{i=0}^3 x_i, \quad \bar{y} = \frac{1}{4} \sum_{i=0}^3 y_i$$
2. Compute polar angle for each vertex:
   $$\theta_i = \text{atan2}(y_i - \bar{y}, x_i - \bar{x})$$
3. Sort points by $\theta_i$ to establish a cyclic loop.
4. Calculate cross-product winding direction and ensure clockwise orientation: $\mathbf{v}_1 \times \mathbf{v}_2 > 0$.
5. Rotate array index such that the point minimizing $x_i + y_i$ is placed at index 0 (Top-Left).

---

## 5. Planar Perspective Transformation (Homography)

### 5.1 Projective Mapping
A planar projective transformation maps source coordinates $\mathbf{x} = [x, y, 1]^T$ to destination coordinates $\mathbf{x}' = [x', y', 1]^T$ via non-singular $3 \times 3$ matrix $\mathbf{H}$:

$$\begin{bmatrix} s x' \\ s y' \\ s \end{bmatrix} = \begin{bmatrix} h_{11} & h_{12} & h_{13} \\ h_{21} & h_{22} & h_{23} \\ h_{31} & h_{32} & h_{33} \end{bmatrix} \begin{bmatrix} x \\ y \\ 1 \end{bmatrix}$$

Because $\mathbf{H}$ has 8 degrees of freedom, 4 point correspondences $\{ (x_i, y_i) \leftrightarrow (x'_i, y'_i) \}_{i=1}^4$ define an exact solution via Direct Linear Transformation (DLT).

```
Source Quadrilateral (Image Plane)           Destination Rectangle (Canvas)
   (TL) p0 ────────── p1 (TR)                  (0,0) ─────────────── (W-1, 0)
     │                 │                         │                       │
     │                 │          =======>       │                       │
     │                 │                         │                       │
   (BL) p3 ────────── p2 (BR)                 (0, H-1) ─────────── (W-1, H-1)
```

### 5.2 Destination Dimensions
$$W = \max\left( \|\mathbf{p}_{\text{TR}} - \mathbf{p}_{\text{TL}}\|_2, \, \|\mathbf{p}_{\text{BR}} - \mathbf{p}_{\text{BL}}\|_2 \right)$$
$$H = \max\left( \|\mathbf{p}_{\text{BL}} - \mathbf{p}_{\text{TL}}\|_2, \, \|\mathbf{p}_{\text{BR}} - \mathbf{p}_{\text{TR}}\|_2 \right)$$

### 5.3 Bicubic Backward Warping
To avoid gaps and aliasing, pixels in the destination grid are mapped backward into source space:
$$\mathbf{x} = \mathbf{H}^{-1} \mathbf{x}'$$
Intensity is interpolated using a bicubic $4 \times 4$ cubic spline kernel (`cv2.INTER_CUBIC`), producing sharp text and anti-aliased edge transitions.

---

## 6. Document Enhancement Filters

| Mode | Function | Purpose |
| :--- | :--- | :--- |
| **Color** | Identity | Retains original colors in the rectified document |
| **Grayscale** | $Y = 0.299R + 0.587G + 0.114B$ | Eliminates color distractions, standard monochrome |
| **Black & White** | Adaptive Gaussian Threshold | Maximizes contrast for printed text and documents |
| **Contrast** | CLAHE on CIE-Lab L* channel | Equalizes illumination variations without color distortion |

### 6.1 Adaptive Gaussian Thresholding
Global thresholding (e.g., fixed value $T = 127$) fails when an image has uneven shadows. Adaptive thresholding computes a local threshold $T(x, y)$ for each pixel using a Gaussian-weighted window of size $B \times B$ ($B = 21$):

$$T(x, y) = \left( \sum_{u, v} G(u, v) \cdot I(x+u, y+v) \right) - C$$

$$\text{dst}(x, y) = \begin{cases} 255 & \text{if } I(x, y) > T(x, y) \\ 0 & \text{otherwise} \end{cases}$$

Here $C = 10$ subtracts background glare to produce crisp black characters on white paper.

### 6.2 Contrast Limited Adaptive Histogram Equalization (CLAHE)
Standard histogram equalization causes over-amplification of noise in homogeneous regions. CLAHE addresses this by:
1. Dividing the image into $8 \times 8$ non-overlapping tiles.
2. Clipping the histogram at limit $\beta = 2.5$.
3. Redistributing clipped pixels uniformly across gray levels.
4. Interpolating across tile boundaries using bilinear interpolation to eliminate grid artifacts.

Applied strictly to the L-channel of CIE-Lab color space:
$$\text{LAB} \to \text{Split}(L, a, b) \to L_{\text{CLAHE}} \to \text{Merge}(L_{\text{CLAHE}}, a, b) \to \text{RGB}$$

---

## 7. Failure Handling & Multi-Stage Fallback Strategy

Real-world photographs may not produce a single clean 4-corner contour under default Canny thresholds. SmartScan implements an automated multi-stage fallback:

1. **Stage 1 (Standard Canny):** Median-adaptive thresholds ($1 \pm 0.33$).
2. **Stage 2 (Sensitive Canny):** Low thresholds ($T_{\text{low}} = 30, T_{\text{high}} = 100$) for documents with faint boundaries.
3. **Stage 3 (Adaptive Thresholding):** Bilateral filtering followed by inverted adaptive thresholding for textured surfaces.
4. **Stage 4 (Otsu Binarization):** Global bimodal thresholding.
5. **Stage 5 (Convex Hull Approximation):** If an 8-point or 12-point jagged contour is found, its convex hull is approximated with Douglas-Peucker.
6. **Graceful Failure & Manual Corner Fallback:** If all automated stages fail, the system returns `detected = false`, prompting the user to place or drag corners directly on the screen.
