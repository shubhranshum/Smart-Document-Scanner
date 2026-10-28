import React, { useState } from 'react';
import { Download, FileText, Image as ImageIcon, Loader2 } from 'lucide-react';
import { downloadFile } from '../utils/imageUtils';
import { exportPdf } from '../services/api';

export default function DownloadPanel({
  originalPreview,
  correctedImage,
  enhancedImage,
  fileMeta,
  isLoading,
}) {
  const [isExportingPdf, setIsExportingPdf] = useState(false);
  const [pdfError, setPdfError] = useState(null);

  const handleDownloadOriginal = () => {
    if (!originalPreview) return;
    downloadFile(originalPreview, `document_original_${fileMeta?.name || 'photo.png'}`);
  };

  const handleDownloadCorrected = () => {
    if (!correctedImage) return;
    downloadFile(correctedImage, 'document_corrected.png');
  };

  const handleDownloadEnhanced = () => {
    if (!enhancedImage) return;
    downloadFile(enhancedImage, 'document_enhanced.png');
  };

  const handleExportPdf = async () => {
    const targetImage = enhancedImage || correctedImage;
    if (!targetImage) return;

    setIsExportingPdf(true);
    setPdfError(null);
    try {
      const blob = await exportPdf({
        imageData: targetImage,
        title: fileMeta?.name ? `Scanned: ${fileMeta.name}` : 'SmartScan Document',
      });
      downloadFile(blob, 'document_scanned.pdf');
    } catch (err) {
      setPdfError(err.message || 'PDF export failed.');
    } finally {
      setIsExportingPdf(false);
    }
  };

  const hasOutput = Boolean(correctedImage || enhancedImage);

  return (
    <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-4 sm:p-5 space-y-3">
      <h2 className="text-sm font-semibold text-slate-800 flex items-center space-x-2">
        <Download className="w-4 h-4 text-blue-600" />
        <span>Export & Downloads</span>
      </h2>

      {pdfError && (
        <p className="text-xs text-rose-500 bg-rose-50 p-2 rounded-lg border border-rose-100">
          {pdfError}
        </p>
      )}

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
        {/* PDF Export */}
        <button
          type="button"
          onClick={handleExportPdf}
          disabled={!hasOutput || isExportingPdf || isLoading}
          className="flex items-center justify-center space-x-2 px-3 py-2.5 rounded-lg text-xs font-semibold bg-rose-600 hover:bg-rose-500 text-white transition disabled:opacity-40 disabled:cursor-not-allowed shadow-xs"
        >
          {isExportingPdf ? (
            <Loader2 className="w-4 h-4 animate-spin" />
          ) : (
            <FileText className="w-4 h-4" />
          )}
          <span>Export Scanned PDF</span>
        </button>

        {/* Enhanced PNG Download */}
        <button
          type="button"
          onClick={handleDownloadEnhanced}
          disabled={!enhancedImage || isLoading}
          className="flex items-center justify-center space-x-2 px-3 py-2.5 rounded-lg text-xs font-semibold bg-blue-600 hover:bg-blue-500 text-white transition disabled:opacity-40 disabled:cursor-not-allowed shadow-xs"
        >
          <ImageIcon className="w-4 h-4" />
          <span>Download Enhanced PNG</span>
        </button>

        {/* Corrected PNG Download */}
        <button
          type="button"
          onClick={handleDownloadCorrected}
          disabled={!correctedImage || isLoading}
          className="flex items-center justify-center space-x-2 px-3 py-2 rounded-lg text-xs font-medium bg-slate-100 hover:bg-slate-200 text-slate-700 transition disabled:opacity-40 disabled:cursor-not-allowed"
        >
          <Download className="w-3.5 h-3.5" />
          <span>Download Straightened PNG</span>
        </button>

        {/* Original Image Download */}
        <button
          type="button"
          onClick={handleDownloadOriginal}
          disabled={!originalPreview || isLoading}
          className="flex items-center justify-center space-x-2 px-3 py-2 rounded-lg text-xs font-medium bg-slate-100 hover:bg-slate-200 text-slate-700 transition disabled:opacity-40 disabled:cursor-not-allowed"
        >
          <Download className="w-3.5 h-3.5" />
          <span>Download Original Image</span>
        </button>
      </div>
    </div>
  );
}
