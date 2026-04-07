import axios from 'axios';

const BASE_URL = import.meta.env.VITE_API_URL;

const api = axios.create({ baseURL: BASE_URL });

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

api.interceptors.response.use(
  (res) => res,
  (err) => {
    if (err.response?.status === 401) {
      localStorage.removeItem('token');
      localStorage.removeItem('username');
      window.location.reload();
    }
    return Promise.reject(err);
  }
);

export const authApi = {
  login: (data) => api.post('/login', data),
  register: (data) => api.post('/register', data),
};

export const documentsApi = {
  list: () => api.get('/documents/'),
  upload: (formData, onProgress) =>
    api.post('/upload-documents/', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
      timeout: 600000,
      onUploadProgress: onProgress,
    }),
  delete: (id) => api.delete(`/documents/${id}`),
};

export const chatApi = {
  send: (payload) => api.post('/chat/', payload),
  getSessions: () => api.get('/chat-sessions/'),
  getHistory: (sessionId) => api.get(`/chat-history/${sessionId}`),
  deleteSession: (sessionId) => api.delete(`/chat-sessions/${sessionId}`),
};

export default api;
