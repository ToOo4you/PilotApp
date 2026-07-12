export const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8001';

async function request(path, options = {}) {
  const res = await fetch(`${API_BASE}${path}`, {
    headers: { 'Content-Type': 'application/json', ...options.headers },
    ...options,
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || `HTTP ${res.status}`);
  }
  return res.json();
}

export const api = {
  generateLesson: (body) =>
    request('/api/education/lesson/generate', { method: 'POST', body: JSON.stringify(body) }),

  tutorChat: (body) =>
    request('/api/education/tutor/chat', { method: 'POST', body: JSON.stringify(body) }),

  generateQuiz: (body) =>
    request('/api/education/quiz/generate', { method: 'POST', body: JSON.stringify(body) }),

  analyzeProgress: (body) =>
    request('/api/education/progress/analyze', { method: 'POST', body: JSON.stringify(body) }),

  health: () => request('/api/education/health'),
};
