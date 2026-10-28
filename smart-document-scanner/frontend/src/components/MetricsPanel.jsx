import React, { useState } from 'react';
import { Activity, ChevronDown, ChevronUp, Clock, Cpu, Maximize2, ShieldCheck } from 'lucide-react';

export default function MetricsPanel({ metrics, detectedCorners, enhancementMode }) {
  const [isOpen, setIsOpen] = useState(true);

  if (!metrics && !detectedCorners) return null;

  return (
    <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-4 sm:p-5">
      <div
        className="flex items-center justify-between cursor-pointer select-none"
        onClick={() => setIsOpen(!isOpen)}
      >
        <h2 className="text-sm font-semibold text-slate-800 flex items-center space-x-2">
          <Activity className="w-4 h-4 text-blue-600" />
          <span>Quantitative Metrics & Diagnostics</span>
        </h2>
        <button type="button" className="text-slate-400 hover:text-slate-600">
          {isOpen ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
        </button>
      </div>

      {isOpen && (
        <div className="mt-4 space-y-3 pt-3 border-t border-slate-100 text-xs">
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
            {/* Detection Method */}
            <div className="bg-slate-50 p-2.5 rounded-lg border border-slate-200">
              <span className="text-[11px] text-slate-500 block mb-0.5">Algorithm Method</span>
              <span className="font-semibold text-slate-800 uppercase tracking-wider">
                {metrics?.method || 'N/A'}
              </span>
            </div>

            {/* Total Duration */}
            <div className="bg-slate-50 p-2.5 rounded-lg border border-slate-200">
              <span className="text-[11px] text-slate-500 block mb-0.5">Processing Time</span>
              <span className="font-semibold text-slate-800 flex items-center space-x-1">
                <Clock className="w-3.5 h-3.5 text-blue-500" />
                <span>
                  {metrics?.totalTimeMs ||
                    metrics?.detectionTimeMs ||
                    metrics?.correctionTimeMs ||
                    0}{' '}
                  ms
                </span>
              </span>
            </div>

            {/* Output Dimensions */}
            <div className="bg-slate-50 p-2.5 rounded-lg border border-slate-200">
              <span className="text-[11px] text-slate-500 block mb-0.5">Rectified Dimensions</span>
              <span className="font-semibold text-slate-800">
                {metrics?.outputWidth && metrics?.outputHeight
                  ? `${metrics.outputWidth} × ${metrics.outputHeight} px`
                  : 'Pending Warp'}
              </span>
            </div>

            {/* Enhancement Filter */}
            <div className="bg-slate-50 p-2.5 rounded-lg border border-slate-200">
              <span className="text-[11px] text-slate-500 block mb-0.5">Enhancement Mode</span>
              <span className="font-semibold text-slate-800 capitalize">
                {enhancementMode.replace('_', ' ')}
              </span>
            </div>
          </div>

          {/* Detailed Corners Coordinate Table */}
          {detectedCorners && detectedCorners.length === 4 && (
            <div className="mt-3">
              <span className="text-[11px] font-medium text-slate-600 block mb-1.5">
                Detected Corner Coordinates (Original Image Space):
              </span>
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
                {detectedCorners.map((pt, i) => {
                  const labels = ['Top-Left (TL)', 'Top-Right (TR)', 'Bottom-Right (BR)', 'Bottom-Left (BL)'];
                  const colors = ['text-blue-600', 'text-purple-600', 'text-orange-600', 'text-teal-600'];
                  return (
                    <div key={i} className="p-2 rounded bg-slate-50 border border-slate-200 font-mono text-[11px]">
                      <div className={`font-semibold text-[10px] mb-0.5 ${colors[i]}`}>{labels[i]}</div>
                      <div className="text-slate-700">
                        X: {Math.round(pt.x)}, Y: {Math.round(pt.y)}
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          )}

          {metrics?.contourArea && (
            <div className="text-[11px] text-slate-500 flex items-center justify-between pt-1">
              <span>Contour Area: {Math.round(metrics.contourArea).toLocaleString()} px²</span>
              {metrics.perimeter && (
                <span>Contour Perimeter: {Math.round(metrics.perimeter).toLocaleString()} px</span>
              )}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
