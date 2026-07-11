const resolveApiBaseUrl = () => {
  const envBaseUrl = import.meta.env.VITE_API_BASE_URL?.trim();
  if (envBaseUrl) {
    return envBaseUrl.replace(/\/$/, '');
  }

  if (typeof window !== 'undefined') {
    const isLocalhost = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1';
    if (isLocalhost) {
      return 'http://127.0.0.1:8000';
    }

    return window.location.origin.replace(/\/$/, '');
  }

  return 'http://127.0.0.1:8000';
};

export const API_BASE_URL = resolveApiBaseUrl();
