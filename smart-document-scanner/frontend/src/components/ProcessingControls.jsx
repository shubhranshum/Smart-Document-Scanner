import React from 'react';
import {
  Scan,
  Sparkles,
  RotateCw,
  RefreshCcw,
  Palette,
  Layers,
  Contrast,
  SunMedium,
  CheckCircle,
} from 'lucide-react';

export default function ProcessingControls({
  file,
  detectedCorners,
  manualCorners,
  correctedImage,
  enhancementMode,
  onDetect,
  onCorrectPerspective,
  onEnhance,
  onAutoProcess,
  onReset,
  isLoading,
}) {
  const hasImage = Boolean(file);
  const hasCorners = Boolean(manualCorners || detectedCorners);
  const hasCorrected = Boolean(correctedImage);

  const enhancementModes = [
    { id: 'color', label: 'Color', icon: Palette, desc: 'Original corrected colors' },
    { id: 'grayscale', label: 'Grayscale', icon: Layers, desc: 'Single channel luminance' },
    { id: 'black_white', label: 'B & W', icon: Contrast, desc: 'Adaptive scan binarization' },
    { id: 'contrast', label: 'Contrast', icon: SunMedium, desc: 'CLAHE local contrast enhancement' },
  ];

  return (
    <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-4 sm:p-5 space-y-4">
      <h2 className="text-sm font-semibold text-slate-800 flex items-center justify-between">
        <span>Processing Pipeline</span>
        {hasCorrected && (
          <span className="text-xs text-emerald-600 font-medium flex items-center space-x-1">
            <CheckCircle className="w-3.5 h-3.5" />
            <span>Ready for Export</span>
          </span>
        )}
      </h2>

      {/* Main Action Buttons */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5">
        {/* Step 1: Detect Document */}
        <button
          type="button"
          onClick={onDetect}
          disabled={!hasImage || isLoading}
          className="flex items-center justify-center space-x-2 px-4 py-2.5 rounded-lg text-xs font-semibold bg-slate-900 hover:bg-slate-800 text-white transition disabled:opacity-40 disabled:cursor-not-allowed shadow-xs"
        >
          <Scan className="w-4 h-4 text-blue-400" />
          <span>1. Detect Document</span>
        </button>

        {/* Step 2: Perspective Correction */}
        <button
          type="button"
          onClick={() => onCorrectPerspective()}
          disabled={!hasCorners || isLoading}
          className="flex items-center justify-center space-x-2 px-4 py-2.5 rounded-lg text-xs font-semibold bg-blue-600 hover:bg-blue-500 text-white transition disabled:opacity-40 disabled:cursor-not-allowed shadow-xs"
        >
          <RotateCw className="w-4 h-4" />
          <span>2. Correct Perspective</span>
        </button>
      </div>

      {/* Quick 1-Click Auto Scan */}
      <button
        type="button"
        onClick={onAutoProcess}
        disabled={!hasImage || isLoading}
        className="w-full flex items-center justify-center space-x-2 px-4 py-2 rounded-lg text-xs font-semibold bg-emerald-600 hover:bg-emerald-500 text-white transition disabled:opacity-40 disabled:cursor-not-allowed shadow-xs"
        title="Runs boundary detection, perspective warping, and enhancement in one step"
      >
        <Sparkles className="w-4 h-4 text-emerald-200" />
        <span>One-Click Smart Scan</span>
      </button>

      {/* Step 3: Enhancement Modes */}
      <div className="pt-2 border-t border-slate-100">
        <label className="text-xs font-medium text-slate-600 mb-2 block">
          3. Document Enhancement Filter:
        </label>
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
          {enhancementModes.map((m) => {
            const Icon = m.icon;
            const isSelected = enhancementMode === m.id;
            return (
              <button
                key={m.id}
                type="button"
                onClick={() => onEnhance(m.id)}
                disabled={!hasCorrected || isLoading}
                title={m.desc}
                className={`flex flex-col items-center justify-center p-2.5 rounded-lg border text-xs font-medium transition ${
                  isSelected
                    ? 'border-blue-600 bg-blue-50/70 text-blue-700 shadow-xs ring-1 ring-blue-600'
                    : 'border-slate-200 bg-slate-50/50 text-slate-600 hover:bg-slate-100'
                } disabled:opacity-40 disabled:cursor-not-allowed`}
              >
                <Icon className={`w-4 h-4 mb-1 ${isSelected ? 'text-blue-600' : 'text-slate-500'}`} />
                <span>{m.label}</span>
              </button>
            );
          })}
        </div>
      </div>

      {/* Reset */}
      <div className="pt-2 border-t border-slate-100 flex justify-end">
        <button
          type="button"
          onClick={onReset}
          disabled={!hasImage || isLoading}
          className="flex items-center space-x-1.5 px-3 py-1.5 text-xs font-medium text-slate-500 hover:text-rose-600 hover:bg-rose-50 rounded-lg transition disabled:opacity-30 disabled:cursor-not-allowed"
        >
          <RefreshCcw className="w-3.5 h-3.5" />
          <span>Reset All</span>
        </button>
      </div>
    </div>
  );
}
