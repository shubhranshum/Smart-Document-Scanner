import React, { useState } from 'react';
import { Columns, Eye, SlidersHorizontal } from 'lucide-react';

export default function ComparisonView({
  originalImage,
  processedImage,
  mode = 'side_by_side',
  onToggleMode,
}) {
  const [sliderPos, setSliderPos] = useState(50); // 0 to 100%

  return (
    <div className="w-full h-full flex flex-col items-center justify-center p-2">
      {/* Comparison Controls */}
      <div className="mb-3 flex items-center space-x-2 bg-white px-3 py-1.5 rounded-lg border border-slate-200 shadow-sm text-xs">
        <span className="font-medium text-slate-700">Comparison Style:</span>
        <button
          type="button"
          onClick={() => onToggleMode('side_by_side')}
          className={`px-2.5 py-1 rounded flex items-center space-x-1 font-medium transition ${
            mode === 'side_by_side'
              ? 'bg-blue-600 text-white shadow-xs'
              : 'text-slate-600 hover:bg-slate-100'
          }`}
        >
          <Columns className="w-3.5 h-3.5" />
          <span>Side by Side</span>
        </button>
        <button
          type="button"
          onClick={() => onToggleMode('split')}
          className={`px-2.5 py-1 rounded flex items-center space-x-1 font-medium transition ${
            mode === 'split'
              ? 'bg-blue-600 text-white shadow-xs'
              : 'text-slate-600 hover:bg-slate-100'
          }`}
        >
          <SlidersHorizontal className="w-3.5 h-3.5" />
          <span>Split Slider</span>
        </button>
      </div>

      {/* Side-by-Side View */}
      {mode === 'side_by_side' ? (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 w-full h-[520px] max-w-5xl">
          {/* Left: Original */}
          <div className="flex flex-col items-center bg-white p-3 rounded-xl border border-slate-200 shadow-sm overflow-hidden">
            <div className="text-xs font-semibold text-slate-700 mb-2 flex items-center space-x-1.5">
              <span className="w-2 h-2 rounded-full bg-slate-400"></span>
              <span>Original Photo (Perspective Distorted)</span>
            </div>
            <div className="flex-1 w-full flex items-center justify-center overflow-hidden">
              <img
                src={originalImage}
                alt="Original"
                className="max-h-[460px] max-w-full object-contain rounded-md"
              />
            </div>
          </div>

          {/* Right: Corrected / Enhanced */}
          <div className="flex flex-col items-center bg-white p-3 rounded-xl border border-slate-200 shadow-sm overflow-hidden">
            <div className="text-xs font-semibold text-slate-700 mb-2 flex items-center space-x-1.5">
              <span className="w-2 h-2 rounded-full bg-emerald-500"></span>
              <span>Straightened & Scanned Document</span>
            </div>
            <div className="flex-1 w-full flex items-center justify-center overflow-hidden">
              <img
                src={processedImage}
                alt="Processed Document"
                className="max-h-[460px] max-w-full object-contain rounded-md"
              />
            </div>
          </div>
        </div>
      ) : (
        /* Split Slider View */
        <div className="relative w-full max-w-2xl h-[500px] bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden flex items-center justify-center">
          {/* Background image: Processed */}
          <img
            src={processedImage}
            alt="Processed"
            className="absolute max-h-[480px] max-w-full object-contain select-none pointer-events-none"
          />

          {/* Foreground clipped image: Original */}
          <div
            className="absolute inset-0 overflow-hidden flex items-center justify-center"
            style={{ clipPath: `inset(0 ${100 - sliderPos}% 0 0)` }}
          >
            <img
              src={originalImage}
              alt="Original"
              className="max-h-[480px] max-w-full object-contain select-none pointer-events-none"
            />
          </div>

          {/* Divider Line */}
          <div
            className="absolute top-0 bottom-0 w-0.5 bg-blue-600 shadow-[0_0_10px_rgba(37,99,235,0.8)] z-10 pointer-events-none"
            style={{ left: `${sliderPos}%` }}
          >
            <div className="absolute top-1/2 -translate-y-1/2 -translate-x-1/2 w-7 h-7 bg-blue-600 text-white rounded-full flex items-center justify-center shadow-lg border-2 border-white">
              <SlidersHorizontal className="w-3.5 h-3.5" />
            </div>
          </div>

          {/* Invisible interactive range input on top */}
          <input
            type="range"
            min="0"
            max="100"
            value={sliderPos}
            onChange={(e) => setSliderPos(Number(e.target.value))}
            className="absolute inset-0 w-full h-full opacity-0 cursor-ew-resize z-20"
          />

          {/* Floating Badges */}
          <div className="absolute bottom-3 left-3 bg-slate-900/80 text-white text-[11px] px-2 py-1 rounded backdrop-blur-xs pointer-events-none">
            Original
          </div>
          <div className="absolute bottom-3 right-3 bg-blue-600/90 text-white text-[11px] px-2 py-1 rounded backdrop-blur-xs pointer-events-none">
            Corrected
          </div>
        </div>
      )}
    </div>
  );
}
