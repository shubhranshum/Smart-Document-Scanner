import { useState, useCallback, useEffect } from 'react';
import {
  detectDocument,
  correctPerspective,
  enhanceImage,
  processPipeline,
  exportPdf,
  checkHealth,
} from '../services/api';
import {
  getImageNaturalDimensions,
  validateImageFile,
  validateCornersGeometry,
} from '../utils/imageUtils';

export function useDocumentScanner() {
  const [file, setFile] = useState(null);
  const [fileMeta, setFileMeta] = useState(null);
  const [originalPreview, setOriginalPreview] = useState(null);

  // Corner coordinates in original image space
  const [detectedCorners, setDetectedCorners] = useState(null);
  const [manualCorners, setManualCorners] = useState(null);
  const [isEditingCorners, setIsEditingCorners] = useState(false);

  // Previews and outputs
  const [annotatedPreview, setAnnotatedPreview] = useState(null);
  const [correctedImage, setCorrectedImage] = useState(null);
  const [enhancedImage, setEnhancedImage] = useState(null);
  const [enhancementMode, setEnhancementMode] = useState('color');

  // UI Navigation & Viewing
  const [activeTab, setActiveTab] = useState('original'); // 'original', 'detection', 'corrected', 'enhanced', 'comparison'
  const [comparisonMode, setComparisonMode] = useState('side_by_side'); // 'side_by_side' | 'single'

  // Processing state
  const [isLoading, setIsLoading] = useState(false);
  const [statusMessage, setStatusMessage] = useState('Upload a document photo to begin.');
  const [error, setError] = useState(null);

  // Diagnostics & Metrics
  const [metrics, setMetrics] = useState(null);
  const [backendHealth, setBackendHealth] = useState({ healthy: false });

  // Initial health check
  useEffect(() => {
    checkHealth().then((health) => {
      setBackendHealth(health);
    });
  }, []);

  // Cleanup object URLs when file changes
  const resetState = useCallback(() => {
    if (originalPreview && originalPreview.startsWith('blob:')) {
      URL.revokeObjectURL(originalPreview);
    }
    setFile(null);
    setFileMeta(null);
    setOriginalPreview(null);
    setDetectedCorners(null);
    setManualCorners(null);
    setIsEditingCorners(false);
    setAnnotatedPreview(null);
    setCorrectedImage(null);
    setEnhancedImage(null);
    setEnhancementMode('color');
    setActiveTab('original');
    setMetrics(null);
    setError(null);
    setStatusMessage('Upload a document photo to begin.');
  }, [originalPreview]);

  // Handle new file selection
  const handleFileUpload = useCallback(
    async (uploadedFile) => {
      const validation = validateImageFile(uploadedFile);
      if (!validation.valid) {
        setError(validation.error);
        return;
      }

      resetState();
      setError(null);
      setIsLoading(true);
      setStatusMessage('Loading and validating image dimensions...');

      try {
        const { width, height } = await getImageNaturalDimensions(uploadedFile);
        const previewUrl = URL.createObjectURL(uploadedFile);

        setFile(uploadedFile);
        setFileMeta({
          name: uploadedFile.name,
          size: uploadedFile.size,
          width,
          height,
        });
        setOriginalPreview(previewUrl);
        setActiveTab('original');
        setStatusMessage('Image uploaded. Ready for document detection.');
      } catch (err) {
        setError(err.message || 'Failed to decode uploaded image.');
      } finally {
        setIsLoading(false);
      }
    },
    [resetState]
  );

  // Detect document corners
  const handleDetect = useCallback(async () => {
    if (!file) return;

    setIsLoading(true);
    setError(null);
    setStatusMessage('Analyzing edges and detecting document boundaries...');

    try {
      const res = await detectDocument(file, true);
      setMetrics({
        detectionTimeMs: res.processing_time_ms,
        method: res.method,
        contourArea: res.contour_area,
        perimeter: res.contour_perimeter,
        imageWidth: res.image_width,
        imageHeight: res.image_height,
      });

      if (res.detected && res.corners) {
        setDetectedCorners(res.corners);
        setManualCorners(res.corners);
        setAnnotatedPreview(res.preview_image);
        if (res.image_width && res.image_height) {
          setFileMeta((prev) => ({
            ...prev,
            width: res.image_width,
            height: res.image_height,
          }));
        }
        setActiveTab('detection');
        setStatusMessage('Document detected! You can adjust corners or proceed with perspective correction.');
      } else {
        setAnnotatedPreview(res.preview_image || originalPreview);
        if (res.image_width && res.image_height) {
          setFileMeta((prev) => ({
            ...prev,
            width: res.image_width,
            height: res.image_height,
          }));
        }
        setActiveTab('detection');
        setIsEditingCorners(true);
        setStatusMessage(
          res.message || 'Automatic detection failed. Please select 4 corners manually.'
        );
      }
    } catch (err) {
      setError(err.message || 'Failed to detect document.');
    } finally {
      setIsLoading(false);
    }
  }, [file, originalPreview]);

  // Correct perspective using current active corners
  const handleCorrectPerspective = useCallback(
    async (customCorners = null) => {
      if (!file) return;

      const cornersToUse = customCorners || manualCorners || detectedCorners;
      if (!cornersToUse || cornersToUse.length !== 4) {
        setError('Valid 4 corners are required for perspective correction.');
        return;
      }

      const geomCheck = validateCornersGeometry(cornersToUse);
      if (!geomCheck.valid) {
        setError(`Cannot warp perspective: ${geomCheck.error}`);
        return;
      }

      setIsLoading(true);
      setError(null);
      setStatusMessage('Applying homography and perspective transformation...');

      try {
        const res = await correctPerspective(file, cornersToUse);
        setCorrectedImage(res.corrected_image);
        setEnhancedImage(res.corrected_image); // Default is color
        setEnhancementMode('color');
        setActiveTab('corrected');
        setMetrics((prev) => ({
          ...prev,
          correctionTimeMs: res.processing_time_ms,
          outputWidth: res.output_width,
          outputHeight: res.output_height,
        }));
        setStatusMessage('Perspective correction completed! Document is straightened.');
      } catch (err) {
        setError(err.message || 'Failed to correct perspective.');
      } finally {
        setIsLoading(false);
      }
    },
    [file, manualCorners, detectedCorners]
  );

  // Apply enhancement mode
  const handleEnhance = useCallback(
    async (mode) => {
      if (!correctedImage) return;

      setEnhancementMode(mode);
      if (mode === 'color') {
        setEnhancedImage(correctedImage);
        setActiveTab('enhanced');
        return;
      }

      setIsLoading(true);
      setError(null);
      setStatusMessage(`Enhancing document (${mode.replace('_', ' ')})...`);

      try {
        const res = await enhanceImage({
          imageData: correctedImage,
          mode,
        });
        setEnhancedImage(res.enhanced_image);
        setActiveTab('enhanced');
        setMetrics((prev) => ({
          ...prev,
          enhancementTimeMs: res.processing_time_ms,
          enhancementMode: res.mode,
        }));
        setStatusMessage(`Document enhanced with ${mode.replace('_', ' ')}.`);
      } catch (err) {
        setError(err.message || 'Failed to enhance image.');
      } finally {
        setIsLoading(false);
      }
    },
    [correctedImage]
  );

  // End-to-end one-click auto process
  const handleAutoProcess = useCallback(async () => {
    if (!file) return;

    setIsLoading(true);
    setError(null);
    setStatusMessage('Running end-to-end scanner pipeline...');

    try {
      const res = await processPipeline(file, enhancementMode, null, true);
      setMetrics({
        totalTimeMs: res.processing_time_ms,
        method: res.detection_method,
        outputWidth: res.output_width,
        outputHeight: res.output_height,
      });

      if (res.detected && res.corners) {
        setDetectedCorners(res.corners);
        setManualCorners(res.corners);
        setAnnotatedPreview(res.annotated_preview);
        setCorrectedImage(res.corrected_image);
        setEnhancedImage(res.enhanced_image);
        setActiveTab('corrected');
        setStatusMessage('Document scanned and perspective-corrected successfully!');
      } else {
        setAnnotatedPreview(res.annotated_preview || originalPreview);
        setActiveTab('detection');
        setIsEditingCorners(true);
        setStatusMessage(res.message || 'Detection failed. Please select corners manually.');
      }
    } catch (err) {
      setError(err.message || 'Processing failed.');
    } finally {
      setIsLoading(false);
    }
  }, [file, enhancementMode, originalPreview]);

  // Corner editing actions
  const startManualCornerEdit = useCallback(() => {
    if (!manualCorners && fileMeta) {
      // Default initial corners inset by 10%
      const w = fileMeta.width;
      const h = fileMeta.height;
      const initial = [
        { x: Math.round(w * 0.1), y: Math.round(h * 0.1) },
        { x: Math.round(w * 0.9), y: Math.round(h * 0.1) },
        { x: Math.round(w * 0.9), y: Math.round(h * 0.9) },
        { x: Math.round(w * 0.1), y: Math.round(h * 0.9) },
      ];
      setManualCorners(initial);
    }
    setIsEditingCorners(true);
    setActiveTab('detection');
  }, [manualCorners, fileMeta]);

  const applyManualCorners = useCallback(() => {
    if (!manualCorners || manualCorners.length !== 4) {
      setError('Please select exactly 4 corners.');
      return;
    }
    const check = validateCornersGeometry(manualCorners);
    if (!check.valid) {
      setError(`Invalid corner coordinates: ${check.error}`);
      return;
    }
    setIsEditingCorners(false);
    setError(null);
    handleCorrectPerspective(manualCorners);
  }, [manualCorners, handleCorrectPerspective]);

  const resetCornersToDetected = useCallback(() => {
    if (detectedCorners) {
      setManualCorners(detectedCorners);
      setError(null);
    }
  }, [detectedCorners]);

  return {
    file,
    fileMeta,
    originalPreview,
    detectedCorners,
    manualCorners,
    setManualCorners,
    isEditingCorners,
    setIsEditingCorners,
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
  };
}
