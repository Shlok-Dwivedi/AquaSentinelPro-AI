// API Configuration
// In development, Vite proxy forwards /api, /static, /uploads to the backend
// In production, this should be set to your deployed backend URL

const API_BASE_URL = import.meta.env.VITE_API_URL || '';

export const API_ENDPOINTS = {
  // Auth
  LOGIN: `${API_BASE_URL}/api/v1/auth/login`,
  REGISTER: `${API_BASE_URL}/api/v1/auth/register`,
  ME: `${API_BASE_URL}/api/v1/auth/me`,
  LOGOUT: `${API_BASE_URL}/api/v1/auth/logout`,

  // Chat
  CHAT_MESSAGE: `${API_BASE_URL}/api/v1/chat/message`,

  // Dashboard
  DASHBOARD: `${API_BASE_URL}/api/v1/analysis/dashboard`,

  // Reports
  REPORTS: `${API_BASE_URL}/api/v1/reports`,
  REPORT_DETAIL: (id) => `${API_BASE_URL}/api/v1/reports/${id}`,
  REPORT_DOWNLOAD: (id, format) => `${API_BASE_URL}/api/v1/reports/download/${id}/${format}`,

  // Health
  HEALTH: `${API_BASE_URL}/health`,
};

export default API_BASE_URL;
