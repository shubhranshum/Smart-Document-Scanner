# IPCV Viva & Oral Examination Questions with Comprehensive Answers

This document contains 30 in-depth viva voce questions and answers prepared specifically for the **Smart Document Scanner** college project defense.

---

### Q1: What is the primary objective of this project?
**Answer:** The objective is to develop an explainable, end-to-end Computer Vision system that takes arbitrary perspective-distorted photographs of physical documents, automatically detects their boundary quadrilateral, applies planar projective rectification (homography) to straighten them into a canonical rectangular view, and enhances their legibility using adaptive thresholding and contrast enhancement.

---

### Q2: Why did you choose classical image processing over deep learning (like YOLO or Mask R-CNN)?
**Answer:** Classical image processing was chosen for three key reasons:
1. **Explainability & Theory:** Techniques like Canny edge detection, Douglas-Peucker polygon approximation, and SVD-based homography are mathematically rigorous and transparent.
2. **Compute Efficiency:** The classical pipeline executes in approximately 4 ms on standard CPU hardware without requiring dedicated GPUs or high memory footprints.
3. **Zero Data Dependency:** Classical algorithms operate directly on differential geometric properties without requiring thousands of labeled training images.

---

### Q3: What is a Homography in Computer Vision?
**Answer:** A homography is an invertible mapping (projectivity) from one projective plane to another, represented by a $3 \times 3$ non-singular matrix $\mathbf{H}$. It maps coplanar points from the camera sensor plane to the rectified document plane:
$$\mathbf{x}' \sim \mathbf{H}\mathbf{x}$$
It preserves collinearity, lines remain lines, and incidence, but does not preserve Euclidean distance or parallelism.

---

### Q4: How many degrees of freedom (DOF) does a 2D homography matrix have?
**Answer:** An arbitrary $3 \times 3$ matrix has 9 elements. However, since homography is defined up to a non-zero projective scale factor ($\mathbf{x}' \sim \mathbf{H}\mathbf{x}$ implies $c\mathbf{H}$ yields the exact same inhomogeneous coordinates), one element acts as a global scale. Therefore, a planar homography has **8 degrees of freedom**.

---

### Q5: Why do we need exactly four point correspondences to compute a homography?
**Answer:** Each point correspondence $(x_i, y_i) \leftrightarrow (x'_i, y'_i)$ gives two independent linear equations:
$$x'_i = \frac{h_{11}x_i + h_{12}y_i + h_{13}}{h_{31}x_i + h_{32}y_i + h_{33}}, \quad y'_i = \frac{h_{21}x_i + h_{22}y_i + h_{23}}{h_{31}x_i + h_{32}y_i + h_{33}}$$
To solve for 8 unknown degrees of freedom, we require at least $8 / 2 = 4$ independent point correspondences (where no three points are collinear).

---

### Q6: How does the Direct Linear Transformation (DLT) algorithm solve for $\mathbf{H}$?
**Answer:** The inhomogeneous equations are rearranged into the homogeneous matrix form $\mathbf{A}\mathbf{h} = \mathbf{0}$, where $\mathbf{A}$ is an $8 \times 9$ coefficient matrix and $\mathbf{h} = [h_{11}, h_{12}, \dots, h_{33}]^T$. We solve this using Singular Value Decomposition (SVD):
$$\mathbf{A} = \mathbf{U} \mathbf{\Sigma} \mathbf{V}^T$$
The optimal least-squares solution $\mathbf{h}$ is the singular vector corresponding to the smallest singular value in $\mathbf{V}$ (the last column of $\mathbf{V}$).

---

### Q7: Explain the steps of the Canny edge detector.
**Answer:** The Canny edge detector consists of 4 main steps:
1. **Gaussian Smoothing:** Convolving the image with a Gaussian kernel to attenuate high-frequency noise.
2. **Gradient Calculation:** Applying Sobel operators ($K_x, K_y$) to compute gradient magnitude $|G|$ and edge direction $\theta$.
3. **Non-Maximum Suppression (NMS):** Thinning edges by suppressing pixels whose gradient magnitude is not a local maximum along the gradient direction.
4. **Hysteresis Thresholding:** Utilizing two thresholds ($T_{\text{high}}$ and $T_{\text{low}}$). Pixels $> T_{\text{high}}$ are strong edges; pixels between $T_{\text{low}}$ and $T_{\text{high}}$ are retained only if connected to strong edges.

---

### Q8: How did you select the threshold values for Canny edge detection?
**Answer:** Rather than hardcoding static thresholds that fail across different lighting conditions, we implemented **auto-Canny**:
$$v = \text{median}(I_{\text{smooth}})$$
$$T_{\text{low}} = \max(0, (1 - \sigma)v), \quad T_{\text{high}} = \min(255, (1 + \sigma)v), \quad \text{with } \sigma = 0.33$$
This tunes the thresholds to the ambient illumination of the scene.

---

### Q9: Why is Gaussian blur necessary before Canny edge detection?
**Answer:** Numerical differentiation (such as the discrete Sobel derivative) is inherently a high-pass filter that amplifies high-frequency noise. Without Gaussian pre-smoothing, noise spikes produce false gradient extrema, resulting in fragmented, spurious edges throughout the background.

---

### Q10: How does the Douglas-Peucker algorithm work?
**Answer:** Douglas-Peucker (`cv2.approxPolyDP`) simplifies a polyline or contour:
1. Draws a line between the curve's first and last points.
2. Finds the point on the curve furthest from this line (distance $d_{\max}$).
3. If $d_{\max} > \epsilon$, the curve is split at that point and the process recurses on both sub-segments.
4. If $d_{\max} \le \epsilon$, all intermediate points are discarded, keeping only the straight segment.
We set $\epsilon = 0.02 \cdot \text{Perimeter}$.

---

### Q11: How do you verify whether a detected 4-point polygon is a valid document quadrilateral?
**Answer:** We enforce four geometric tests:
1. **Vertex count:** Must have exactly 4 vertices.
2. **Convexity:** Adjacent edge cross-products must all have the same sign (`cv2.isContourConvex`).
3. **Distinct points:** Euclidean distance between any pair of points must exceed 5 pixels.
4. **No self-intersection:** Bow-tie / hourglass quadrilaterals are rejected.
5. **Area threshold:** Enclosed area must exceed 5% of the total photograph canvas.

---

### Q12: Why is corner ordering important before applying perspective transformation?
**Answer:** `cv2.getPerspectiveTransform` associates the $i$-th source point with the $i$-th destination point:
- Index 0 $\to (0, 0)$ [Top-Left]
- Index 1 $\to (W-1, 0)$ [Top-Right]
- Index 2 $\to (W-1, H-1)$ [Bottom-Right]
- Index 3 $\to (0, H-1)$ [Bottom-Left]
If the source corners are out of order, the warped output will be upside-down, mirrored, or twisted into an inverted triangle.

---

### Q13: How did you implement corner ordering?
**Answer:** We compute the centroid $(\bar{x}, \bar{y})$ of the 4 points, sort the points angularly using $\text{atan2}(y_i - \bar{y}, x_i - \bar{x})$, check edge cross-product signs to ensure clockwise winding, and circularly shift the indices so that the point with the minimal sum $x_i + y_i$ is placed at index 0 (Top-Left).

---

### Q14: How are the destination width and height computed?
**Answer:** By taking the maximum Euclidean distance of opposing edges:
$$W = \max(\|\mathbf{p}_{\text{TR}} - \mathbf{p}_{\text{TL}}\|_2, \|\mathbf{p}_{\text{BR}} - \mathbf{p}_{\text{BL}}\|_2)$$
$$H = \max(\|\mathbf{p}_{\text{BL}} - \mathbf{p}_{\text{TL}}\|_2, \|\mathbf{p}_{\text{BR}} - \mathbf{p}_{\text{TR}}\|_2)$$
This preserves the aspect ratio and resolution of the document without arbitrary stretching.

---

### Q15: What interpolation method is used during perspective warping and why?
**Answer:** We use **bicubic interpolation** (`cv2.INTER_CUBIC`). While nearest-neighbor produces aliasing and bilinear interpolation softens sharp edges, bicubic considers a $4 \times 4$ neighborhood using cubic polynomial weighting, preserving crisp text strokes and high-frequency legibility.

---

### Q16: Why is forward warping problematic, and how does backward warping solve it?
**Answer:** In forward mapping, source pixels $(x, y)$ are projected to destination $(x', y')$. Because $x'$ and $y'$ are real numbers, rounding to integer grid points leads to "holes" (unmapped destination pixels) and "collisions" (multiple source pixels mapped to one destination pixel). 
**Backward mapping** solves this by iterating through every discrete pixel in the destination canvas, applying $\mathbf{H}^{-1}$ to find its continuous location in the source image, and interpolating its intensity from surrounding source pixels.

---

### Q17: What is Adaptive Thresholding, and why is it preferred over Otsu or global thresholding for scanned documents?
**Answer:** Global thresholding sets a single threshold $T$ for the entire image. In real-world photos, shadows cast across a page make the shadowed white paper darker than the brightly lit black ink on the other side. Adaptive thresholding computes a localized threshold $T(x, y)$ within a small Gaussian window ($21 \times 21$), dynamically adapting to localized lighting variations.

---

### Q18: What is CLAHE, and how does it differ from standard Histogram Equalization?
**Answer:** Standard Global Histogram Equalization flattens the intensity histogram across the entire image, which over-amplifies background noise and washes out text. **CLAHE** (Contrast Limited Adaptive Histogram Equalization) operates on small tiles ($8 \times 8$), clips the local histogram at a contrast limit (2.5) to prevent over-enhancement, redistributes the excess pixels uniformly, and blends tile boundaries using bilinear interpolation.

---

### Q19: Why downsample the image before running contour detection?
**Answer:** Modern smartphone cameras take 12 to 48 megapixel images ($4000 \times 3000+$). Running Canny and contour extraction on full-resolution images takes hundreds of milliseconds and detects microscopic paper grain. Downsampling to a max dimension of 1000 px reduces computation time by over 90% while isolating macro document boundaries. The detected coordinates are then scaled back to original resolution.

---

### Q20: How do you map coordinates between the downscaled image and original image?
**Answer:** If the image was downscaled by factors $s_x = W_{\text{resized}} / W_{\text{orig}}$ and $s_y = H_{\text{resized}} / H_{\text{orig}}$, any coordinate $(x_r, y_r)$ in the detection image is transformed back via:
$$x_{\text{orig}} = \frac{x_r}{s_x}, \quad y_{\text{orig}} = \frac{y_r}{s_y}$$
This ensures the final homography warp runs on the pristine, full-resolution source image.

---

### Q21: What happens if automatic document detection fails?
**Answer:** In low-contrast scenes (e.g., white paper on white desk), classical edge detection cannot find 4 clean corners. SmartScan treats detection failure as an expected physical scenario rather than a crash. The API returns `detected: false`, and the UI seamlessly unlocks an interactive SVG corner editor where users can drag corner handles or click 4 points directly on the preview.

---

### Q22: How does the SVG corner editor remain synchronized when the browser window is resized?
**Answer:** The SVG overlay uses a standardized responsive coordinate mapping `viewBox="0 0 1000 1000"` with `preserveAspectRatio="none"`. Relative pointer coordinates $[0, 1]$ on the display element are converted to original image coordinates by multiplying by `originalWidth` and `originalHeight`. This decouples user interaction from display CSS styling.

---

### Q23: How do you handle EXIF orientation in smartphone photos?
**Answer:** Smartphone cameras often store the raw sensor raster in landscape and rely on an EXIF orientation metadata flag (e.g., Tag 274) to indicate portrait rotation. OpenCV's `imread` historically ignores EXIF, leading to sideways processing. We use Pillow's `ImageOps.exif_transpose` to physically reorient pixel buffers into standard upright orientation prior to OpenCV processing.

---

### Q24: What metrics did you use to evaluate your detection algorithm?
**Answer:** We used three metrics:
1. **Detection Success Rate:** Percentage of test images where a valid 4-point quadrilateral was identified.
2. **Mean Corner Error ($E_{\text{mean}}$):** Average Euclidean distance (in pixels) between detected corners and ground truth corners:
   $$E_{\text{mean}} = \frac{1}{4} \sum_{i=1}^4 \|\mathbf{p}_{\text{detected}, i} - \mathbf{p}_{\text{GT}, i}\|_2$$
3. **Normalized Corner Error:** $E_{\text{mean}}$ divided by the image diagonal $\sqrt{W^2 + H^2}$, enabling resolution-independent comparison.

---

### Q25: What was the measured performance of your system on the benchmark dataset?
**Answer:** On the 10-case synthetic benchmark dataset:
- Detection Success Rate: **100.0%**
- Mean Corner Error: **1.41 pixels**
- Normalized Corner Error: **0.100%**
- Average Detection Latency: **4.11 ms**

---

### Q26: What are the main limitations of this system?
**Answer:**
1. **Planar assumption:** Assumes documents are flat planes. Curved book spines or heavily creased paper cannot be fully corrected with a single 2D homography matrix.
2. **Low-contrast boundaries:** Fails if the document background matches the paper color exactly.
3. **Severe occlusions:** Objects covering corners (hands, pens) prevent 4-vertex polygonal approximation.

---

### Q27: How does your system prevent memory exhaustion (DoS attacks) from large image uploads?
**Answer:** The backend enforces three safety barriers:
1. Upload payload size limit of 15 MB.
2. Maximum decoded image pixel limit of 25 megapixels (rejects decompression bombs).
3. Maximum rectified output pixel limit of 16 megapixels.

---

### Q28: How is PDF export implemented without relying on external system tools?
**Answer:** We implemented PDF generation in Python using the `reportlab` library. The rectified image is converted into an in-memory JPEG stream and embedded onto a standard A4 portrait page with proportional aspect ratio scaling and 0.5-inch margins, returning binary PDF bytes directly to the client.

---

### Q29: What is the difference between an affine transformation and a perspective transformation?
**Answer:** An affine transformation has 6 degrees of freedom, preserves parallelism (parallel lines remain parallel), and represents orthographic projection with rotation, translation, scaling, and shear. A perspective transformation (homography) has 8 degrees of freedom, does not preserve parallelism, and models central projection through a pinhole camera where parallel lines converge at vanishing points.

---

### Q30: What future improvements could be added to this project?
**Answer:**
1. Mesh-based non-rigid dewarping (Thin-Plate Splines) to straighten curved book pages.
2. Direct OCR text recognition using Tesseract to produce searchable, copyable PDFs.
3. Compiling the core C++ OpenCV pipeline to WebAssembly (Wasm) for complete client-side in-browser scanning.
