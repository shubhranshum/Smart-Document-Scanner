import React, { useState } from 'react';
import Header from '../components/Header';
import UploadPanel from '../components/UploadPanel';
import ImageWorkspace from '../components/ImageWorkspace';
import ProcessingControls from '../components/ProcessingControls';
import DownloadPanel from '../components/DownloadPanel';
import MetricsPanel from '../components/MetricsPanel';
import InfoModal from '../components/InfoModal';
import { useDocumentScanner } from '../hooks/useDocumentScanner';
import { AlertCircle } from 'lucide-react';

export default function Home() {
  const [isInfoModalOpen, setIsInfoModalOpen] = useState(false);

  const {
    file,
    fileMeta,
    originalPreview,
    detectedCorners,
    manualCorners,
    setManualCorners,
    isEditingCorners,
    annotatedPreview,
    correctedImage,
    enhancedImage,
    enhancementMode,
    activeTab,
    setActiveTab,
    comparisonMode,
    setComparisonMode,
    isLoading,
    statusMessage,
    error,
    metrics,
    backendHealth,
    handleFileUpload,
    handleDetect,
    handleCorrectPerspective,
    handleEnhance,
    handleAutoProcess,
    startManualCornerEdit,
    applyManualCorners,
    resetCornersToDetected,
    resetState,
    setIsEditingCorners,
  } = useDocumentScanner();

  return (
    <div className="min-h-screen flex flex-col bg-slate-100/60 font-sans">
      {/* Top Application Bar */}
      <Header
        backendHealth={backendHealth}
        isLoading={isLoading}
        onOpenInfo={() => setIsInfoModalOpen(true)}
      />

      {/* Main Container */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6 flex-1 w-full flex flex-col space-y-5">
        {/* Error Alert Banner */}
        {error && (
          <div className="bg-rose-50 border border-rose-200 text-rose-700 px-4 py-3 rounded-xl flex items-center space-x-3 text-xs shadow-xs animate-in fade-in duration-200">
            <AlertCircle className="w-4 h-4 flex-shrink-0 text-rose-500" />
            <div className="flex-1 font-medium">{error}</div>
          </div>
        )}

        {/* 2-Column Responsive Layout */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
          {/* Left Controls Sidebar (5 Cols on Large) */}
          <div className="lg:col-span-5 space-y-5">
            <UploadPanel
              file={file}
              fileMeta={fileMeta}
              originalPreview={originalPreview}
              onFileUpload={handleFileUpload}
              onReset={resetState}
              isLoading={isLoading}
            />

            <ProcessingControls
              file={file}
              detectedCorners={detectedCorners}
              manualCorners={manualCorners}
              correctedImage={correctedImage}
              enhancementMode={enhancementMode}
              onDetect={handleDetect}
              onCorrectPerspective={handleCorrectPerspective}
              onEnhance={handleEnhance}
              onAutoProcess={handleAutoProcess}
              onReset={resetState}
              isLoading={isLoading}
            />

            <DownloadPanel
              originalPreview={originalPreview}
              correctedImage={correctedImage}
              enhancedImage={enhancedImage}
              fileMeta={fileMeta}
              isLoading={isLoading}
            />

            <MetricsPanel
              metrics={metrics}
              detectedCorners={manualCorners || detectedCorners}
              enhancementMode={enhancementMode}
            />
          </div>

          {/* Right Main Workspace (7 Cols on Large) */}
          <div className="lg:col-span-7">
            <ImageWorkspace
              file={file}
              fileMeta={fileMeta}
              originalPreview={originalPreview}
              annotatedPreview={annotatedPreview}
              correctedImage={correctedImage}
              enhancedImage={enhancedImage}
              activeTab={activeTab}
              onTabChange={setActiveTab}
              isEditingCorners={isEditingCorners}
              onStartEditingCorners={startManualCornerEdit}
              onCancelEditingCorners={() => setIsEditingCorners(false)}
              manualCorners={manualCorners}
              onCornersChange={setManualCorners}
              onApplyManualCorners={applyManualCorners}
              onResetCorners={resetCornersToDetected}
              statusMessage={statusMessage}
              isLoading={isLoading}
              comparisonMode={comparisonMode}
              onToggleComparisonMode={setComparisonMode}
            />
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="border-t border-slate-200 bg-white py-4 mt-8">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex flex-col sm:flex-row items-center justify-between text-xs text-slate-500 gap-2">
          <span>SmartScan &bull; Image Processing & Computer Vision Project</span>
          <span>OpenCV &bull; Homography & Perspective Transformation &bull; FastAPI &bull; React</span>
        </div>
      </footer>

      {/* Educational Guide Modal */}
      <InfoModal
        isOpen={isInfoModalOpen}
        onClose={() => setIsInfoModalOpen(false)}
      />
    </div>
  );
}
