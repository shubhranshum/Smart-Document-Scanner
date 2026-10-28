import React from 'react';
import { Scan, HelpCircle, Info, CheckCircle2, AlertCircle, RefreshCw } from 'lucide-react';

export default function Header({ backendHealth, isLoading, onOpenInfo, onOpenAbout }) {
  return (
    <header className="bg-white border-b border-slate-200 sticky top-0 z-30 shadow-sm">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        {/* Brand */}
        <div className="flex items-center space-x-3">
          <div className="w-10 h-10 rounded-xl bg-blue-600 flex items-center justify-center text-white shadow-md shadow-blue-500/20">
            <Scan className="w-6 h-6" />
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <span className="text-xl font-bold tracking-tight text-slate-900">SmartScan</span>
              <span className="text-xs px-2 py-0.5 rounded-full font-medium bg-blue-50 text-blue-700 border border-blue-200">
                IPCV Edition
              </span>
            </div>
            <p className="text-xs text-slate-500 hidden sm:block">
              Document Detection & Perspective Homography Correction
            </p>
          </div>
        </div>

        {/* Status & Actions */}
        <div className="flex items-center space-x-4">
          {/* Processing Indicator */}
          {isLoading && (
            <div className="flex items-center space-x-2 text-xs font-medium text-blue-600 bg-blue-50 px-3 py-1.5 rounded-full border border-blue-100 animate-pulse">
              <RefreshCw className="w-3.5 h-3.5 animate-spin" />
              <span>Processing...</span>
            </div>
          )}

          {/* Backend Status Pill */}
          <div
            className={`flex items-center space-x-1.5 px-3 py-1 rounded-full text-xs font-medium border ${
              backendHealth.healthy
                ? 'bg-emerald-50 text-emerald-700 border-emerald-200'
                : 'bg-amber-50 text-amber-700 border-amber-200'
            }`}
            title={backendHealth.healthy ? `OpenCV ${backendHealth.opencv_version}` : 'Backend offline'}
          >
            {backendHealth.healthy ? (
              <>
                <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600" />
                <span>Backend Connected</span>
              </>
            ) : (
              <>
                <AlertCircle className="w-3.5 h-3.5 text-amber-600" />
                <span>Backend Offline</span>
              </>
            )}
          </div>

          {/* Educational / Info Buttons */}
          <button
            onClick={onOpenInfo}
            className="flex items-center space-x-1 px-3 py-1.5 text-xs font-medium text-slate-600 hover:text-blue-600 hover:bg-slate-100 rounded-lg transition"
            title="How the Image Processing Algorithm Works"
          >
            <HelpCircle className="w-4 h-4" />
            <span className="hidden md:inline">How It Works</span>
          </button>
        </div>
      </div>
    </header>
  );
}
