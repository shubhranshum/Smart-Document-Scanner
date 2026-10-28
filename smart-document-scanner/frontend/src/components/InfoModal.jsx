import React from 'react';
import { X, BookOpen, Layers, Cpu, Scan, CheckCircle, ArrowRight } from 'lucide-react';

export default function InfoModal({ isOpen, onClose }) {
  if (!isOpen) return null;

  const steps = [
    {
      step: '1',
      title: 'Preprocessing & Grayscale Conversion',
      desc: 'The RGB input image is converted to grayscale using Y = 0.299R + 0.587G + 0.114B to remove chrominance variations. A 5x5 Gaussian blur filter is applied to suppress high-frequency noise and texture while preserving dominant structural edges.',
      formula: 'G(x, y) = \\frac{1}{2\\pi\\sigma^2} e^{-\\frac{x^2+y^2}{2\\sigma^2}}',
    },
    {
      step: '2',
      title: 'Canny Edge Detection & Morphology',
      desc: 'The Canny algorithm computes spatial intensity gradients using Sobel operators, applies non-maximum suppression to thin edges, and uses hysteresis thresholding with dual thresholds to link strong and weak edges. Morphological closing connects minor perimeter discontinuities.',
      formula: '|\\nabla I| = \\sqrt{I_x^2 + I_y^2}, \\quad \\theta = \\arctan(I_y / I_x)',
    },
    {
      step: '3',
      title: 'Contour Extraction & Filtering',
      desc: 'Topological boundaries are extracted using Suzuki’s border following algorithm (cv2.findContours). Contours are sorted by enclosed area, discarding any candidate occupying less than 5% of the total photograph area.',
      formula: 'A = \\frac{1}{2} \\sum_{i=0}^{n-1} (x_i y_{i+1} - x_{i+1} y_i)',
    },
    {
      step: '4',
      title: 'Douglas-Peucker Polygon Approximation',
      desc: 'Promising candidate contours are simplified using the Douglas-Peucker algorithm (cv2.approxPolyDP) with an epsilon of 0.02 * perimeter. Only convex polygons that yield exactly 4 distinct vertices and do not self-intersect are retained.',
      formula: '\\epsilon = 0.02 \\cdot \\text{Perimeter}',
    },
    {
      step: '5',
      title: 'Corner Ordering & Perspective Homography',
      desc: 'The four corner coordinates are deterministically sorted clockwise [Top-Left, Top-Right, Bottom-Right, Bottom-Left]. Destination rectangle dimensions (W, H) are computed from opposing Euclidean edge norms. A 3x3 homography matrix H is computed via Direct Linear Transformation (DLT) and applied using cv2.warpPerspective.',
      formula: 's \\begin{bmatrix} x\' \\\\ y\' \\\\ 1 \\end{bmatrix} = \\mathbf{H} \\begin{bmatrix} x \\\\ y \\\\ 1 \\end{bmatrix}',
    },
    {
      step: '6',
      title: 'Document Enhancement Filtering',
      desc: 'The straightened document is enhanced for readability: Color preserves the true perspective-corrected image, Grayscale extracts luminance, Black & White applies Gaussian adaptive thresholding for laser-sharp printed text, and Contrast applies CLAHE to the CIE-Lab L-channel.',
      formula: 'T(x, y) = \\text{Mean}_{\\text{local}}(x, y) - C',
    },
  ];

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-xs">
      <div className="bg-white rounded-2xl border border-slate-200 shadow-2xl max-w-3xl w-full max-h-[85vh] flex flex-col overflow-hidden animate-in fade-in zoom-in-95 duration-150">
        {/* Header */}
        <div className="px-6 py-4 border-b border-slate-200 flex items-center justify-between bg-slate-50">
          <div className="flex items-center space-x-2">
            <BookOpen className="w-5 h-5 text-blue-600" />
            <h3 className="text-base font-bold text-slate-800">
              How SmartScan Works: Image Processing Pipeline
            </h3>
          </div>
          <button
            onClick={onClose}
            className="p-1 rounded-lg text-slate-400 hover:text-slate-600 hover:bg-slate-200/60 transition"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content */}
        <div className="p-6 overflow-y-auto space-y-5">
          <p className="text-xs text-slate-600 leading-relaxed">
            SmartScan is built on explainable classical Image Processing and Computer Vision (IPCV)
            principles. Rather than relying on black-box neural networks, it utilizes deterministic
            differential edge filters, contour topology, and planar projective geometry:
          </p>

          <div className="space-y-4">
            {steps.map((st) => (
              <div
                key={st.step}
                className="flex items-start space-x-3.5 p-3.5 rounded-xl bg-slate-50 border border-slate-200/80"
              >
                <div className="w-7 h-7 rounded-lg bg-blue-600 text-white font-bold text-xs flex items-center justify-center flex-shrink-0 mt-0.5 shadow-xs">
                  {st.step}
                </div>
                <div className="flex-1 min-w-0">
                  <h4 className="text-xs font-bold text-slate-800">{st.title}</h4>
                  <p className="text-xs text-slate-600 mt-1 leading-normal">{st.desc}</p>
                  <div className="mt-2 px-2.5 py-1 bg-white rounded border border-slate-200 inline-block font-mono text-[11px] text-blue-700">
                    {st.formula}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Footer */}
        <div className="px-6 py-3 border-t border-slate-200 bg-slate-50 flex justify-end">
          <button
            type="button"
            onClick={onClose}
            className="px-4 py-2 rounded-lg bg-blue-600 hover:bg-blue-500 text-white text-xs font-semibold shadow-xs transition"
          >
            Close Guide
          </button>
        </div>
      </div>
    </div>
  );
}
