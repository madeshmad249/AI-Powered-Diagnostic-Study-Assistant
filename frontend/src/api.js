const API_BASE = '/api';

export async function apiRequest(endpoint, options = {}) {
  const token = localStorage.getItem('gapfinder_token') || 'Bearer user_1';
  const headers = {
    'Content-Type': 'application/json',
    'Authorization': token,
    ...(options.headers || {})
  };

  if (options.body instanceof FormData) {
    delete headers['Content-Type']; // Let browser set boundary
  }

  const response = await fetch(`${API_BASE}${endpoint}`, {
    ...options,
    headers
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({ detail: 'Request failed' }));
    throw new Error(errorData.detail || `HTTP ${response.status}`);
  }

  return response.json();
}

export const api = {
  // Auth
  demoLogin: () => apiRequest('/auth/demo-login', { method: 'POST' }),
  login: (email, password) => apiRequest('/auth/login', {
    method: 'POST',
    body: JSON.stringify({ email, password })
  }),
  getMe: () => apiRequest('/auth/me'),

  // Documents
  listDocuments: () => apiRequest('/documents'),
  uploadDocument: (file, docType) => {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('doc_type', docType);
    return apiRequest('/documents/upload', {
      method: 'POST',
      body: formData
    });
  },

  // Topics
  getTopics: () => apiRequest('/topics'),
  generateTopicMap: () => apiRequest('/topics/generate-map', { method: 'POST' }),

  // Diagnostic Quiz
  generateQuiz: (topicId, questionCount = 3) => apiRequest('/quiz/generate', {
    method: 'POST',
    body: JSON.stringify({ topic_id: topicId, question_count: questionCount })
  }),
  submitQuiz: (topicId, answers) => apiRequest('/quiz/submit', {
    method: 'POST',
    body: JSON.stringify({ topic_id: topicId, answers })
  }),

  // Gap Report
  getGapReport: () => apiRequest('/diagnostic/gap-report'),

  // Revision Plan
  getRevisionPlan: () => apiRequest('/revision-plan'),
  generateRevisionPlan: (targetDays, dailyHours) => apiRequest('/revision-plan/generate', {
    method: 'POST',
    body: JSON.stringify({ target_days: targetDays, daily_hours: dailyHours })
  }),

  // Grounded Tutor Chat
  explainTopic: (topicName, userQuery = null) => apiRequest('/tutor/explain', {
    method: 'POST',
    body: JSON.stringify({ topic_name: topicName, user_query: userQuery })
  }),

  // Dashboard
  getDashboardMetrics: () => apiRequest('/dashboard/metrics')
};
