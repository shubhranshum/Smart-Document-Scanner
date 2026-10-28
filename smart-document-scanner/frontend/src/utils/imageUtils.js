/**
 * Utilities for image validation, coordinate scaling, and geometry checks.
 */

export const MAX_FILE_SIZE_BYTES = 15 * 1024 * 1024; // 15MB
export const ACCEPTED_FILE_TYPES = ['image/jpeg', 'image/png', 'image/webp'];

export function formatFileSize(bytes) {
  if (bytes === 0) return '0 B';
  const k = 1024;
  const sizes = ['B', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return `${parseFloat((bytes / Math.pow(k, i)).toFixed(2))} ${sizes[i]}`;
}

export function validateImageFile(file) {
  if (!file) {
    return { valid: false, error: 'No file selected.' };
  }
  if (!ACCEPTED_FILE_TYPES.includes(file.type)) {
    return {
      valid: false,
      error: `Unsupported file format (${file.type || 'unknown'}). Please upload JPG, PNG, or WEBP.`
    };
  }
  if (file.size > MAX_FILE_SIZE_BYTES) {
    return {
      valid: false,
      error: `File size (${formatFileSize(file.size)}) exceeds maximum limit of 15 MB.`
    };
  }
  return { valid: true, error: null };
}

export function getImageNaturalDimensions(file) {
  return new Promise((resolve, reject) => {
    const img = new Image();
    const url = URL.createObjectURL(file);
    img.onload = () => {
      const width = img.naturalWidth;
      const height = img.naturalHeight;
      URL.revokeObjectURL(url);
      resolve({ width, height });
    };
    img.onerror = (err) => {
      URL.revokeObjectURL(url);
      reject(new Error('Failed to load image for dimension extraction.'));
    };
    img.src = url;
  });
}

/**
 * Validates whether 4 points form a convex, non-self-intersecting quadrilateral.
 */
export function validateCornersGeometry(points) {
  if (!points || points.length !== 4) {
    return { valid: false, error: 'Exactly 4 points are required.' };
  }

  // Check minimum edge distance
  for (let i = 0; i < 4; i++) {
    for (let j = i + 1; j < 4; j++) {
      const dx = points[i].x - points[j].x;
      const dy = points[i].y - points[j].y;
      if (Math.hypot(dx, dy) < 5) {
        return { valid: false, error: 'Points cannot overlap.' };
      }
    }
  }

  // Check cross products of consecutive edges for convexity and winding consistency
  const crossProducts = [];
  for (let i = 0; i < 4; i++) {
    const pPrev = points[(i + 3) % 4];
    const pCurr = points[i];
    const pNext = points[(i + 1) % 4];

    const v1 = { x: pCurr.x - pPrev.x, y: pCurr.y - pPrev.y };
    const v2 = { x: pNext.x - pCurr.x, y: pNext.y - pCurr.y };
    const cp = v1.x * v2.y - v1.y * v2.x;
    crossProducts.push(cp);
  }

  const signs = crossProducts.map((cp) => Math.sign(cp)).filter((s) => Math.abs(s) > 0);
  if (signs.length < 4) {
    return { valid: false, error: 'Points are collinear or degenerate.' };
  }

  const allPositive = signs.every((s) => s > 0);
  const allNegative = signs.every((s) => s < 0);
  if (!allPositive && !allNegative) {
    return { valid: false, error: 'Points form a self-intersecting or non-convex shape.' };
  }

  return { valid: true, error: null };
}

/**
 * Downloads a Blob or DataURL as a file with the given name.
 */
export function downloadFile(urlOrBlob, filename) {
  const isBlob = urlOrBlob instanceof Blob;
  const url = isBlob ? URL.createObjectURL(urlOrBlob) : urlOrBlob;

  const a = document.createElement('a');
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);

  if (isBlob) {
    setTimeout(() => URL.revokeObjectURL(url), 1000);
  }
}
