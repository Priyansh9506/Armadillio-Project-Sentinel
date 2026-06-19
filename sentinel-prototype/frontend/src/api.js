import axios from 'axios';

const API_BASE = 'http://localhost:8000/api';

const api = axios.create({
  baseURL: API_BASE,
  headers: { 'Content-Type': 'application/json' },
});

// Attach JWT token to every request
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('sentinel_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Auto-refresh token on 401
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;
    if (error.response && error.response.status === 401 && !originalRequest._retry && originalRequest.url !== '/auth/login') {
      originalRequest._retry = true;
      try {
        const refreshToken = localStorage.getItem('sentinel_refresh_token');
        if (!refreshToken) throw new Error('No refresh token');
        
        const res = await axios.post(`${API_BASE}/auth/refresh`, { refresh_token: refreshToken });
        if (res.data.token) {
          localStorage.setItem('sentinel_token', res.data.token);
          originalRequest.headers.Authorization = `Bearer ${res.data.token}`;
          return api(originalRequest);
        }
      } catch (err) {
        localStorage.clear();
        window.location.href = '/';
      }
    }
    return Promise.reject(error);
  }
);

// ─── Auth ──────────────────────────────────────────────────
export const authAPI = {
  register: (data) => api.post('/auth/register', data),
  login: (data) => api.post('/auth/login', data),
  logout: (data) => api.post('/auth/logout', data),
  refresh: (data) => api.post('/auth/refresh', data),
};

// ─── Telemetry ─────────────────────────────────────────────
export const telemetryAPI = {
  ingest: (data) => api.post('/telemetry/ingest', data),
};

// ─── MFA ───────────────────────────────────────────────────
export const mfaAPI = {
  initiatePushAuth: (data) => api.post('/mfa/push-auth/initiate', data),
  verifyPushAuth: (data) => api.post('/mfa/push-auth/verify', data),
  getVoicePhrase: () => api.get('/mfa/voice-liveness/phrase'),
  verifyVoice: (data) => api.post('/mfa/voice-liveness/verify', data),
  duressTransfer: (data) => api.post('/mfa/duress-transfer', data),
};

// ─── SOC ───────────────────────────────────────────────────
export const socAPI = {
  getAlerts: (limit = 20) => api.get(`/soc/alerts?limit=${limit}`),
  getTrustLogs: (userId, limit = 50) =>
    api.get(`/soc/trust-logs?${userId ? `user_id=${userId}&` : ''}limit=${limit}`),
  getSessions: () => api.get('/soc/sessions'),
  getStats: () => api.get('/soc/stats'),
  getFraudGraph: () => api.get('/graph/fraud-ring'),
};

export default api;
