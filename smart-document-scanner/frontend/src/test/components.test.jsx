import { describe, it, expect, vi } from 'vitest';
import React from 'react';
import { render, screen } from '@testing-library/react';
import Header from '../components/Header';
import ProcessingControls from '../components/ProcessingControls';
import UploadPanel from '../components/UploadPanel';

describe('Frontend Component Tests', () => {
  it('renders Header with status and title', () => {
    render(
      <Header
        backendHealth={{ healthy: true, opencv_version: '4.11.0' }}
        isLoading={false}
        onOpenInfo={() => {}}
      />
    );
    expect(screen.getByText('SmartScan')).toBeInTheDocument();
    expect(screen.getByText('Backend Connected')).toBeInTheDocument();
  });

  it('renders UploadPanel empty state', () => {
    render(
      <UploadPanel
        file={null}
        fileMeta={null}
        originalPreview={null}
        onFileUpload={() => {}}
        onReset={() => {}}
        isLoading={false}
      />
    );
    expect(screen.getByText(/Click to upload or drag & drop/i)).toBeInTheDocument();
  });

  it('disables processing controls when no image is loaded', () => {
    render(
      <ProcessingControls
        file={null}
        detectedCorners={null}
        manualCorners={null}
        correctedImage={null}
        enhancementMode="color"
        onDetect={() => {}}
        onCorrectPerspective={() => {}}
        onEnhance={() => {}}
        onAutoProcess={() => {}}
        onReset={() => {}}
        isLoading={false}
      />
    );

    const detectBtn = screen.getByRole('button', { name: /1\. Detect Document/i });
    expect(detectBtn).toBeDisabled();

    const correctBtn = screen.getByRole('button', { name: /2\. Correct Perspective/i });
    expect(correctBtn).toBeDisabled();
  });
});
