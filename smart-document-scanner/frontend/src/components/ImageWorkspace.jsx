import React, { useRef } from 'react';
import { Eye, Scan, FileCheck, Wand2, Split, Edit3 } from 'lucide-react';
import CornerEditor from './CornerEditor';
import ComparisonView from './ComparisonView';

export default function ImageWorkspace({
  file,
  fileMeta,
  originalPreview,
  annotatedPreview,
  correctedImage,
  enhancedImage,
  activeTab,
  onTabChange,
  isEditingCorners,
  onStartEditingCorners,
  onCancelEditingCorners,
  manualCorners,
  onCornersChange,
  onApplyManualCorners,
  onResetCorners,
  statusMessage,
  isLoading,
  comparisonMode,
  onToggleComparisonMode,
}) {
  const imageContainerRef = useRef(null);

  // Tab configuration
  const tabs = [
    { id: 'original', label: 'Original', icon: Eye, available: Boolean(originalPreview) },
    { id: 'detection', label: 'Detection', icon: Scan, available: Boolean(originalPreview) },
    { id: 'corrected', label: 'Corrected', icon: FileCheck, available: Boolean(correctedImage) },
    { id: 'enhanced', label: 'Enhanced', icon: Wand2, available: Boolean(enhancedImage) },
    { id: 'comparison', label: 'Comparison', icon: Split, available: Boolean(correctedImage) },
  ];

  if (!file) {
    return (
      <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-12 text-center flex flex-col items-center justify-center min-h-[480px]">
        <div className="w-16 h-16 rounded-2xl bg-slate-100 flex items-center justify-center text-slate-400 mb-4 border border-slate-200">
          <Scan className="w-8 h-8" />
        </div>
        <h3 className="text-base font-semibold text-slate-700">Workspace Empty</h3>
        <p className="text-sm text-slate-500 max-w-sm mt-1">
          Please upload a photo of a document using the upload panel to begin boundary detection and perspective correction.
        </p>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden flex flex-col">
      {/* Workspace Header with Tabs */}
      <div className="border-b border-slate-200 bg-slate-50/70 px-4 py-2.5 flex flex-wrap items-center justify-between gap-3">
        {/* Navigation Tabs */}
        <div className="flex items-center space-x-1 overflow-x-auto">
          {tabs.map((tab) => {
            const Icon = tab.icon;
            const isActive = activeTab === tab.id;
            return (
              <button
                key={tab.id}
                type="button"
                onClick={() => tab.available && onTabChange(tab.id)}
                disabled={!tab.available || isLoading}
                className={`flex items-center space-x-1.5 px-3 py-1.5 rounded-lg text-xs font-medium transition ${
                  isActive
                    ? 'bg-white text-blue-600 shadow-sm border border-slate-200 font-semibold'
                    : tab.available
                    ? 'text-slate-600 hover:text-slate-900 hover:bg-slate-200/50'
                    : 'text-slate-300 cursor-not-allowed'
                }`}
              >
                <Icon className="w-3.5 h-3.5" />
                <span>{tab.label}</span>
              </button>
            );
          })}
        </div>

        {/* Workspace Quick Actions */}
        <div className="flex items-center space-x-2">
          {activeTab === 'detection' && !isEditingCorners && (
            <button
              type="button"
              onClick={onStartEditingCorners}
              disabled={isLoading}
              className="px-2.5 py-1 text-xs font-medium rounded-md bg-blue-50 text-blue-700 hover:bg-blue-100 border border-blue-200 transition flex items-center space-x-1"
            >
              <Edit3 className="w-3.5 h-3.5" />
              <span>Adjust Corners</span>
            </button>
          )}
        </div>
      </div>

      {/* Main Viewport Container */}
      <div
        ref={imageContainerRef}
        className="relative flex-1 min-h-[460px] max-h-[640px] bg-slate-900/5 flex items-center justify-center p-4 overflow-hidden"
      >
        {/* 1. Comparison Tab View */}
        {activeTab === 'comparison' && correctedImage ? (
          <ComparisonView
            originalImage={originalPreview}
            processedImage={enhancedImage || correctedImage}
            mode={comparisonMode}
            onToggleMode={onToggleComparisonMode}
          />
        ) : (
          /* Single Image Display Area */
          <div className="relative max-w-full max-h-full flex items-center justify-center">
            {/* Active Image Tag */}
            {activeTab === 'original' && originalPreview && (
              <img
                src={originalPreview}
                alt="Original Document"
                className="max-h-[580px] max-w-full object-contain rounded-lg shadow-sm"
              />
            )}

            {activeTab === 'detection' && (
              <div className="relative inline-block">
                <img
                  src={originalPreview}
                  alt="Detection View"
                  className="max-h-[580px] max-w-full object-contain rounded-lg shadow-sm block select-none pointer-events-none"
                />
                {/* Interactive Corner Editor & Crisp Vector Boundary Overlay */}
                {(isEditingCorners || manualCorners) && fileMeta && (
                  <CornerEditor
                    corners={manualCorners}
                    originalWidth={fileMeta.width}
                    originalHeight={fileMeta.height}
                    containerRef={imageContainerRef}
                    onCornersChange={onCornersChange}
                    onApply={onApplyManualCorners}
                    onReset={onResetCorners}
                    onCancel={onCancelEditingCorners}
                    disabled={isLoading}
                  />
                )}
              </div>
            )}

            {activeTab === 'corrected' && correctedImage && (
              <img
                src={correctedImage}
                alt="Corrected Perspective Document"
                className="max-h-[580px] max-w-full object-contain rounded-lg shadow-md"
              />
            )}

            {activeTab === 'enhanced' && enhancedImage && (
              <img
                src={enhancedImage}
                alt="Enhanced Scanned Document"
                className="max-h-[580px] max-w-full object-contain rounded-lg shadow-md"
              />
            )}
          </div>
        )}
      </div>

      {/* Workspace Footer Status Bar */}
      <div className="px-4 py-2 bg-slate-50 border-t border-slate-200 flex items-center justify-between text-xs text-slate-500">
        <span className="truncate">{statusMessage}</span>
        {fileMeta && (
          <span className="flex-shrink-0 text-slate-400">
            {fileMeta.width} &times; {fileMeta.height} px
          </span>
        )}
      </div>
    </div>
  );
}
