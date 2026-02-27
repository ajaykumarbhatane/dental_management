import axios from 'axios';
import Cookies from 'js-cookie';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  withCredentials: true,
});

// Request interceptor - Add JWT token from cookies
api.interceptors.request.use(
  (config) => {
    const token = Cookies.get('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor - Handle 401 and other errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Token expired or invalid - logout user
      Cookies.remove('access_token');
      Cookies.remove('refresh_token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// ============================================
// AUTHENTICATION SERVICES
// ============================================

export const authService = {
  login: (email, password) =>
    api.post('/auth/login/', { email, password }),

  logout: () =>
    api.post('/auth/logout/'),

  refresh: () =>
    api.post('/auth/refresh/'),

  me: () =>
    api.get('/auth/me/'),

  register: (data) =>
    api.post('/auth/register/', data),
};

// ============================================
// PATIENTS SERVICES
// ============================================

export const patientService = {
  getAll: (params) =>
    api.get('/patients/', { params }),

  getById: (id) =>
    api.get(`/patients/${id}/`),

  create: (data) =>
    api.post('/patients/', data),

  update: (id, data) =>
    api.patch(`/patients/${id}/`, data),

  delete: (id) =>
    api.delete(`/patients/${id}/`),

  search: (query) =>
    api.get('/patients/', { params: { search: query } }),

  uploadImage: (patientId, file) => {
    const formData = new FormData();
    formData.append('image', file);
    return api.post(`/patients/${patientId}/upload-image/`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
  },
};

// ============================================
// TREATMENTS SERVICES
// ============================================

export const treatmentService = {
  getAll: (params) =>
    api.get('/treatments/', { params }),

  getById: (id) =>
    api.get(`/treatments/${id}/`),

  create: (data) => {
    // If data is FormData (e.g., with file upload), don't set Content-Type header
    // Axios will auto-set the boundary headers; this avoids conflicts
    if (data instanceof FormData) {
      return api.post('/treatments/', data, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
    }
    return api.post('/treatments/', data);
  },

  update: (id, data) =>
    api.patch(`/treatments/${id}/`, data),

  delete: (id) =>
    api.delete(`/treatments/${id}/`),

  uploadImage: (treatmentId, file) => {
    const formData = new FormData();
    formData.append('image', file);
    return api.post(`/treatments/${treatmentId}/upload-image/`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
  },
};

// ============================================
// CLINICS SERVICES
// ============================================

export const clinicService = {
  getAll: (params) =>
    api.get('/clinics/', { params }),

  getById: (id) =>
    api.get(`/clinics/${id}/`),

  update: (id, data) =>
    api.patch(`/clinics/${id}/`, data),
};

// ============================================
// USER SERVICES
// ============================================

export const userService = {
  getDoctors: () => api.get('/auth/doctors/'),
};

export default api;
