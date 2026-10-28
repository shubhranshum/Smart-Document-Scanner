import React, { useState, useRef, useEffect, useCallback } from 'react';
import { Check, RotateCcw, X, AlertTriangle, Crosshair } from 'lucide-react';
import { validateCornersGeometry } from '../utils/imageUtils';

const CORNER_CONFIG = [
  { key: 'tl', label: 'TL', fullLabel: 'Top-Left', color: '#2563eb' },
  { key: 'tr', label: 'TR', fullLabel: 'Top-Right', color: '#9333ea' },
  { key: 'br', label: 'BR', fullLabel: 'Bottom-Right', color: '#ea580c' },
  { key: 'bl', label: 'BL', fullLabel: 'Bottom-Left', color: '#0d9488' },
];

export default function CornerEditor({
  corners, // [{x, y}, {x, y}, {x, y}, {x, y}] in original image coordinates
  originalWidth,
  originalHeight,
  containerRef,
  onCornersChange,
  onApply,
  onReset,
  onCancel,
  disabled = false,
}) {
  const [activeCornerIdx, setActiveCornerIdx] = useState(null);
  const [clickCollectMode, setClickCollectMode] = useState(false);
  const [collectedPoints, setCollectedPoints] = useState([]);
  const [validationError, setValidationError] = useState(null);
  const svgRef = useRef(null);

  // Validate corners on change
  useEffect(() => {
    if (corners && corners.length === 4) {
      const check = validateCornersGeometry(corners);
      setValidationError(check.valid ? null : check.error);
    } else {
      setValidationError(null);
    }
  }, [corners]);

  // Convert image coord (origX, origY) -> SVG viewBox coord [0..1000]
  // Using viewBox="0 0 1000 1000" or direct SVG percentages makes SVG perfectly responsive!
  const toSvgX = useCallback(
    (origX) => {
      if (!originalWidth) return 0;
      return (origX / originalWidth) * 1000;
    },
    [originalWidth]
  );

  const toSvgY = useCallback(
    (origY) => {
      if (!originalHeight) return 0;
      return (origY / originalHeight) * 1000;
    },
    [originalHeight]
  );

  const fromSvgX = useCallback(
    (svgX) => {
      return Math.round((svgX / 1000) * originalWidth);
    },
    [originalWidth]
  );

  const fromSvgY = useCallback(
    (svgY) => {
      return Math.round((svgY / 1000) * originalHeight);
    },
    [originalHeight]
  );

  // Mouse / Touch Dragging Logic
  const handlePointerDown = (index, e) => {
    if (disabled || clickCollectMode) return;
    e.preventDefault();
    e.stopPropagation();
    setActiveCornerIdx(index);
  };

  const handlePointerMove = useCallback(
    (e) => {
      if (activeCornerIdx === null || !svgRef.current || disabled) return;
      e.preventDefault();

      const rect = svgRef.current.getBoundingClientRect();
      const clientX = e.touches ? e.touches[0].clientX : e.clientX;
      const clientY = e.touches ? e.touches[0].clientY : e.clientY;

      // Calculate relative 0..1 position within SVG
      const relX = Math.max(0, Math.min(1, (clientX - rect.left) / rect.width));
      const relY = Math.max(0, Math.min(1, (clientY - rect.top) / rect.height));

      const newOrigX = Math.round(relX * originalWidth);
      const newOrigY = Math.round(relY * originalHeight);

      const updated = corners.map((pt, idx) => {
        if (idx === activeCornerIdx) {
          return { x: newOrigX, y: newOrigY };
        }
        return pt;
      });

      onCornersChange(updated);
    },
    [activeCornerIdx, corners, disabled, originalWidth, originalHeight, onCornersChange]
  );

  const handlePointerUp = useCallback(() => {
    setActiveCornerIdx(null);
  }, []);

  useEffect(() => {
    if (activeCornerIdx !== null) {
      window.addEventListener('pointermove', handlePointerMove);
      window.addEventListener('pointerup', handlePointerUp);
      window.addEventListener('touchmove', handlePointerMove, { passive: false });
      window.addEventListener('touchend', handlePointerUp);
      return () => {
        window.removeEventListener('pointermove', handlePointerMove);
        window.removeEventListener('pointerup', handlePointerUp);
        window.removeEventListener('touchmove', handlePointerMove);
        window.removeEventListener('touchend', handlePointerUp);
      };
    }
  }, [activeCornerIdx, handlePointerMove, handlePointerUp]);

  // Click 4 points mode
  const handleSvgClick = (e) => {
    if (!clickCollectMode || !svgRef.current) return;
    const rect = svgRef.current.getBoundingClientRect();
    const relX = Math.max(0, Math.min(1, (e.clientX - rect.left) / rect.width));
    const relY = Math.max(0, Math.min(1, (e.clientY - rect.top) / rect.height));

    const newPt = {
      x: Math.round(relX * originalWidth),
      y: Math.round(relY * originalHeight),
    };

    const newPts = [...collectedPoints, newPt];
    setCollectedPoints(newPts);

    if (newPts.length === 4) {
      onCornersChange(newPts);
      setClickCollectMode(false);
      setCollectedPoints([]);
    }
  };

  const start4PointClickMode = () => {
    setClickCollectMode(true);
    setCollectedPoints([]);
  };

  const cancel4PointClickMode = () => {
    setClickCollectMode(false);
    setCollectedPoints([]);
  };

  // Build SVG polygon points attribute string
  const polygonPointsStr =
    corners && corners.length === 4
      ? corners.map((p) => `${toSvgX(p.x)},${toSvgY(p.y)}`).join(' ')
      : '';

  return (
    <div className="absolute inset-0 pointer-events-none select-none z-10 flex flex-col justify-between">
      {/* SVG Canvas overlay mapped to image exact bounding box */}
      <svg
        ref={svgRef}
        viewBox="0 0 1000 1000"
        preserveAspectRatio="none"
        onClick={handleSvgClick}
        className={`w-full h-full absolute inset-0 ${
          clickCollectMode ? 'pointer-events-auto cursor-crosshair' : 'pointer-events-none'
        }`}
      >
        {/* Fill polygon */}
        {polygonPointsStr && !clickCollectMode && (
          <polygon
            points={polygonPointsStr}
            fill="#10b981"
            fillOpacity="0.2"
            stroke={validationError ? '#ef4444' : '#10b981'}
            strokeWidth="4"
            strokeDasharray={validationError ? '8 4' : 'none'}
          />
        )}

        {/* Temporary collected points in click mode */}
        {clickCollectMode &&
          collectedPoints.map((pt, i) => (
            <circle
              key={i}
              cx={toSvgX(pt.x)}
              cy={toSvgY(pt.y)}
              r="14"
              fill="#2563eb"
              stroke="#ffffff"
              strokeWidth="4"
            />
          ))}

        {/* 4 Interactive Corner Handles */}
        {!clickCollectMode &&
          corners &&
          corners.length === 4 &&
          corners.map((corner, idx) => {
            const config = CORNER_CONFIG[idx] || CORNER_CONFIG[0];
            const sx = toSvgX(corner.x);
            const sy = toSvgY(corner.y);
            const isActive = activeCornerIdx === idx;

            return (
              <g
                key={config.key}
                className="pointer-events-auto cursor-grab active:cursor-grabbing"
                onPointerDown={(e) => handlePointerDown(idx, e)}
              >
                {/* Touch/mouse hit target */}
                <circle cx={sx} cy={sy} r="32" fill="transparent" />

                {/* Outer halo */}
                <circle
                  cx={sx}
                  cy={sy}
                  r={isActive ? '22' : '18'}
                  fill="white"
                  stroke={config.color}
                  strokeWidth="4"
                  filter="drop-shadow(0 2px 4px rgba(0,0,0,0.3))"
                />

                {/* Inner color center */}
                <circle cx={sx} cy={sy} r={isActive ? '10' : '8'} fill={config.color} />

                {/* Corner Label */}
                <text
                  x={sx}
                  y={sy - 24}
                  textAnchor="middle"
                  fill={config.color}
                  fontSize="28"
                  fontWeight="bold"
                  stroke="#ffffff"
                  strokeWidth="6"
                  paintOrder="stroke fill"
                >
                  {config.label}
                </text>
              </g>
            );
          })}
      </svg>

      {/* Editor Controls Bar */}
      <div className="relative z-20 m-3 p-2 bg-slate-900/90 backdrop-blur-md rounded-xl text-white shadow-xl pointer-events-auto flex flex-wrap items-center justify-between gap-3 text-xs">
        <div className="flex items-center space-x-2">
          {clickCollectMode ? (
            <div className="flex items-center space-x-2 text-amber-300">
              <Crosshair className="w-4 h-4 animate-spin" />
              <span>
                Click corner {collectedPoints.length + 1} of 4 on the document (TL &rarr; TR &rarr; BR &rarr; BL)
              </span>
            </div>
          ) : validationError ? (
            <div className="flex items-center space-x-1.5 text-rose-400">
              <AlertTriangle className="w-4 h-4" />
              <span>{validationError}</span>
            </div>
          ) : (
            <div className="flex items-center space-x-2">
              <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
              <span className="text-slate-300">
                Drag handles to fine-tune document perimeter
              </span>
            </div>
          )}
        </div>

        <div className="flex items-center space-x-2">
          {clickCollectMode ? (
            <button
              onClick={cancel4PointClickMode}
              className="px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 transition"
            >
              Cancel 4-Point Mode
            </button>
          ) : (
            <>
              <button
                type="button"
                onClick={start4PointClickMode}
                className="px-2.5 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 transition flex items-center space-x-1"
                title="Click 4 points manually"
              >
                <Crosshair className="w-3.5 h-3.5" />
                <span>Pick 4 Points</span>
              </button>

              <button
                type="button"
                onClick={onReset}
                className="px-2.5 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 transition flex items-center space-x-1"
                title="Reset corners"
              >
                <RotateCcw className="w-3.5 h-3.5" />
                <span>Reset</span>
              </button>

              <button
                type="button"
                onClick={onCancel}
                className="px-2.5 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 transition"
              >
                Cancel
              </button>

              <button
                type="button"
                onClick={onApply}
                disabled={Boolean(validationError) || disabled}
                className="px-3 py-1.5 rounded-lg bg-blue-600 hover:bg-blue-500 disabled:opacity-50 text-white font-medium transition flex items-center space-x-1 shadow-sm"
              >
                <Check className="w-3.5 h-3.5" />
                <span>Apply & Straighten</span>
              </button>
            </>
          )}
        </div>
      </div>
    </div>
  );
}
