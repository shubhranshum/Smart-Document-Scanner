const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

async function handleResponse(response) {
  if (!response.ok) {
    let errorMessage = `HTTP error! status: ${response.status}`;
    try {
      const errorData = await response.json();
      if (errorData.detail) {
        errorMessage = errorData.detail;
      }
    } catch {
      // Non-JSON error body
    }
    throw new Error(errorMessage);
  }
  return response.json();
}

export async function checkHealth() {
  try {
    const res = await fetch(`${API_BASE}/api/health`);
    if (!res.ok) return { healthy: false };
    const data = await res.json();
    return { healthy: true, ...data };
  } catch (err) {
    return { healthy: false, error: err.message };
  }
}

export async function detectDocument(file, includeDiagnostics = false) {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('include_diagnostics', includeDiagnostics.toString());

  const response = await fetch(`${API_BASE}/api/detect`, {
    method: 'POST',
    body: formData,
  });
  return handleResponse(response);
}

export async function correctPerspective(file, corners, targetWidth = null, targetHeight = null) {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('corners', JSON.stringify(corners));
  if (targetWidth) formData.append('target_width', targetWidth.toString());
  if (targetHeight) formData.append('target_height', targetHeight.toString());

  const response = await fetch(`${API_BASE}/api/correct`, {
    method: 'POST',
    body: formData,
  });
  return handleResponse(response);
}

export async function enhanceImage({ file = null, imageData = null, mode = 'color' }) {
  const formData = new FormData();
  if (file) formData.append('file', file);
  if (imageData) formData.append('image_data', imageData);
  formData.append('mode', mode);

  const response = await fetch(`${API_BASE}/api/enhance`, {
    method: 'POST',
    body: formData,
  });
  return handleResponse(response);
}

export async function processPipeline(file, mode = 'color', corners = null, includeDiagnostics = false) {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('enhancement_mode', mode);
  if (corners) {
    formData.append('corners', JSON.stringify(corners));
  }
  formData.append('include_diagnostics', includeDiagnostics.toString());

  const response = await fetch(`${API_BASE}/api/process`, {
    method: 'POST',
    body: formData,
  });
  return handleResponse(response);
}

export async function exportPdf({ file = null, imageData = null, title = 'SmartScan Document' }) {
  const formData = new FormData();
  if (file) formData.append('file', file);
  if (imageData) formData.append('image_data', imageData);
  formData.append('title', title);

  const response = await fetch(`${API_BASE}/api/export/pdf`, {
    method: 'POST',
    body: formData,
  });

  if (!response.ok) {
    throw new Error('Failed to generate PDF document.');
  }

  return response.blob();
}
