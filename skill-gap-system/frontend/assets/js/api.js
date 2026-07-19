/**
 * Thin fetch() wrapper for the Graduate Skill Gap Prediction System API.
 * Stores the JWT in localStorage and attaches it to every request.
 */
const API = (() => {
  // Change this if the backend runs on a different host/port.
  const BASE_URL = window.API_BASE_URL || 'http://localhost:8000';
  const TOKEN_KEY = 'sgs_token';
  const USER_KEY = 'sgs_user';

  function getToken() {
    return localStorage.getItem(TOKEN_KEY);
  }

  function setSession(token, user) {
    localStorage.setItem(TOKEN_KEY, token);
    if (user) localStorage.setItem(USER_KEY, JSON.stringify(user));
  }

  function clearSession() {
    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem(USER_KEY);
  }

  function getUser() {
    const raw = localStorage.getItem(USER_KEY);
    return raw ? JSON.parse(raw) : null;
  }

  function isAuthenticated() {
    return !!getToken();
  }

  async function request(path, { method = 'GET', body, auth = true, params } = {}) {
    let url = `${BASE_URL}${path}`;
    if (params) {
      const query = new URLSearchParams(params).toString();
      if (query) url += `?${query}`;
    }

    const headers = { 'Content-Type': 'application/json' };
    if (auth && getToken()) {
      headers['Authorization'] = `Bearer ${getToken()}`;
    }

    let response;
    try {
      response = await fetch(url, {
        method,
        headers,
        body: body ? JSON.stringify(body) : undefined,
      });
    } catch (networkError) {
      throw new ApiError('Could not reach the server. Is the backend running?', 0, null);
    }

    if (response.status === 401) {
      clearSession();
      if (!location.pathname.endsWith('login.html')) {
        window.location.href = 'login.html';
      }
    }

    const contentType = response.headers.get('content-type') || '';
    const data = contentType.includes('application/json') ? await response.json().catch(() => null) : null;

    if (!response.ok) {
      const message = (data && (data.detail || data.message)) || `Request failed (${response.status})`;
      throw new ApiError(message, response.status, data);
    }

    return data;
  }

  class ApiError extends Error {
    constructor(message, status, data) {
      super(message);
      this.status = status;
      this.data = data;
    }
  }

  return {
    // Auth
    register: (payload) => request('/api/auth/register', { method: 'POST', body: payload, auth: false }),
    login: (payload) => request('/api/auth/login-json', { method: 'POST', body: payload, auth: false }),
    me: () => request('/api/auth/me'),
    forgotPassword: (email) => request('/api/auth/forgot-password', { method: 'POST', body: { email }, auth: false }),

    // Graduate
    getMyGraduateProfile: () => request('/api/graduates/me'),
    updateMyGraduateProfile: (payload) => request('/api/graduates/me', { method: 'PUT', body: payload }),
    addMySkill: (skillId, proficiency) =>
      request('/api/graduates/me/skills', { method: 'POST', body: { skill_id: skillId, proficiency } }),

    // Skills / reference data
    listSkills: () => request('/api/skills'),
    listUniversities: () => request('/api/universities'),
    listCourses: () => request('/api/courses'),

    // Jobs
    listJobs: (params) => request('/api/jobs', { params }),
    getJobMatch: (jobId) => request(`/api/jobs/${jobId}/match`),

    // Prediction
    runPrediction: () => request('/api/prediction/me', { method: 'POST' }),
    predictionHistory: () => request('/api/prediction/me/history'),

    // Recommendations
    generateRecommendations: () => request('/api/recommendations/me/generate', { method: 'POST' }),
    myRecommendations: () => request('/api/recommendations/me'),

    // Analytics (admin/researcher)
    analyticsOverview: () => request('/api/analytics/overview'),

    // Reports (admin/researcher)
    generateReport: (fileFormat) =>
      request('/api/reports/analytics', { method: 'POST', params: { file_format: fileFormat } }),
    myReports: () => request('/api/reports/me'),
    reportDownloadUrl: (reportId) => `${BASE_URL}/api/reports/${reportId}/download`,

    // Session helpers
    setSession,
    clearSession,
    getUser,
    isAuthenticated,
    ApiError,
  };
})();
