import React, { useRef, useState } from 'react';
import { UploadCloud, FileImage, X, RefreshCw, AlertTriangle } from 'lucide-react';
import { formatFileSize, ACCEPTED_FILE_TYPES } from '../utils/imageUtils';

export default function UploadPanel({
  file,
  fileMeta,
  originalPreview,
  onFileUpload,
  onReset,
  isLoading,
}) {
  const [isDragOver, setIsDragOver] = useState(false);
  const fileInputRef = useRef(null);

  const handleDragEnter = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragOver(true);
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragOver(false);
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    e.stopPropagation();
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragOver(false);

    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      onFileUpload(e.dataTransfer.files[0]);
    }
  };

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files.length > 0) {
      onFileUpload(e.target.files[0]);
    }
  };

  return (
    <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-4 sm:p-5">
      <div className="flex items-center justify-between mb-3">
        <h2 className="text-sm font-semibold text-slate-800 flex items-center space-x-2">
          <UploadCloud className="w-4 h-4 text-blue-600" />
          <span>Document Input</span>
        </h2>
        {file && (
          <span className="text-xs px-2 py-0.5 rounded bg-emerald-50 text-emerald-700 font-medium">
            Loaded
          </span>
        )}
      </div>

      {!file ? (
        <div
          onDragEnter={handleDragEnter}
          onDragLeave={handleDragLeave}
          onDragOver={handleDragOver}
          onDrop={handleDrop}
          onClick={() => fileInputRef.current?.click()}
          className={`border-2 border-dashed rounded-xl p-6 text-center cursor-pointer transition flex flex-col items-center justify-center min-h-[160px] ${
            isDragOver
              ? 'border-blue-500 bg-blue-50/50 scale-[0.99]'
              : 'border-slate-300 hover:border-blue-400 bg-slate-50/60 hover:bg-slate-50'
          }`}
        >
          <input
            type="file"
            ref={fileInputRef}
            onChange={handleFileChange}
            accept={ACCEPTED_FILE_TYPES.join(',')}
            className="hidden"
          />
          <div className="w-12 h-12 rounded-full bg-blue-100 flex items-center justify-center text-blue-600 mb-3">
            <UploadCloud className="w-6 h-6" />
          </div>
          <p className="text-sm font-medium text-slate-700">
            Click to upload or drag & drop document photo
          </p>
          <p className="text-xs text-slate-400 mt-1">
            JPG, PNG, or WEBP up to 15 MB
          </p>
        </div>
      ) : (
        <div className="space-y-3">
          <div className="flex items-center justify-between p-3 rounded-lg bg-slate-50 border border-slate-200">
            <div className="flex items-center space-x-3 overflow-hidden">
              <div className="w-10 h-10 rounded-md bg-white border border-slate-200 overflow-hidden flex-shrink-0 flex items-center justify-center">
                {originalPreview ? (
                  <img
                    src={originalPreview}
                    alt="Thumbnail"
                    className="w-full h-full object-cover"
                  />
                ) : (
                  <FileImage className="w-5 h-5 text-slate-400" />
                )}
              </div>
              <div className="min-w-0">
                <p className="text-xs font-semibold text-slate-800 truncate" title={fileMeta?.name}>
                  {fileMeta?.name}
                </p>
                <p className="text-[11px] text-slate-500">
                  {formatFileSize(fileMeta?.size || 0)} &bull; {fileMeta?.width || 0} &times; {fileMeta?.height || 0} px
                </p>
              </div>
            </div>

            <div className="flex items-center space-x-1">
              <button
                type="button"
                onClick={() => fileInputRef.current?.click()}
                disabled={isLoading}
                className="p-1.5 text-slate-500 hover:text-blue-600 hover:bg-white rounded-md transition"
                title="Replace image"
              >
                <RefreshCw className="w-4 h-4" />
              </button>
              <button
                type="button"
                onClick={onReset}
                disabled={isLoading}
                className="p-1.5 text-slate-500 hover:text-rose-600 hover:bg-white rounded-md transition"
                title="Remove image"
              >
                <X className="w-4 h-4" />
              </button>
            </div>
          </div>
          <input
            type="file"
            ref={fileInputRef}
            onChange={handleFileChange}
            accept={ACCEPTED_FILE_TYPES.join(',')}
            className="hidden"
          />
        </div>
      )}
    </div>
  );
}
