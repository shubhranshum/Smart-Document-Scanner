import { describe, it, expect } from 'vitest';
import {
  formatFileSize,
  validateCornersGeometry,
  validateImageFile,
} from '../utils/imageUtils';

describe('imageUtils', () => {
  it('formats file sizes accurately', () => {
    expect(formatFileSize(0)).toBe('0 B');
    expect(formatFileSize(1024)).toBe('1 KB');
    expect(formatFileSize(1024 * 1024 * 2.5)).toBe('2.5 MB');
  });

  it('validates convex quadrilateral points', () => {
    const validSquare = [
      { x: 0, y: 0 },
      { x: 100, y: 0 },
      { x: 100, y: 100 },
      { x: 0, y: 100 },
    ];
    const res = validateCornersGeometry(validSquare);
    expect(res.valid).toBe(true);
    expect(res.error).toBeNull();
  });

  it('rejects self-intersecting / bow-tie points', () => {
    const bowtie = [
      { x: 0, y: 0 },
      { x: 100, y: 100 },
      { x: 100, y: 0 },
      { x: 0, y: 100 },
    ];
    const res = validateCornersGeometry(bowtie);
    expect(res.valid).toBe(false);
    expect(res.error).toContain('self-intersecting or non-convex');
  });

  it('rejects collinear or degenerate points', () => {
    const collinear = [
      { x: 0, y: 0 },
      { x: 50, y: 0 },
      { x: 100, y: 0 },
      { x: 150, y: 0 },
    ];
    const res = validateCornersGeometry(collinear);
    expect(res.valid).toBe(false);
  });

  it('validates image files by type and size limit', () => {
    const validFile = new File(['dummy content'], 'doc.jpg', { type: 'image/jpeg' });
    expect(validateImageFile(validFile).valid).toBe(true);

    const textFile = new File(['hello'], 'doc.txt', { type: 'text/plain' });
    expect(validateImageFile(textFile).valid).toBe(false);
  });
});
