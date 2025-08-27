import axios from 'axios';
import { toast } from 'react-hot-toast';

// API Configuration
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

// Create axios instance
const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000, // 30 seconds
  headers: {
    'Content-Type': 'application/json',
  },
});

// Auth token management
const getAuthToken = () => localStorage.getItem('authToken');
const setAuthToken = (token) => localStorage.setItem('authToken', token);
const removeAuthToken = () => localStorage.removeItem('authToken');

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    const token = getAuthToken();
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      removeAuthToken();
      window.location.href = '/login';
      toast.error('Session expired. Please login again.');
    } else if (error.response?.status >= 500) {
      toast.error('Server error. Please try again later.');
    }
    return Promise.reject(error);
  }
);

// ============================================================================
// AUTH API
// ============================================================================

export const authAPI = {
  register: async (userData) => {
    const response = await api.post('/auth/register', userData);
    if (response.data.access_token) {
      setAuthToken(response.data.access_token);
    }
    return response.data;
  },

  login: async (credentials) => {
    const response = await api.post('/auth/login', credentials);
    if (response.data.access_token) {
      setAuthToken(response.data.access_token);
    }
    return response.data;
  },

  logout: () => {
    removeAuthToken();
    window.location.href = '/login';
  },

  getProfile: async () => {
    const response = await api.get('/auth/profile');
    return response.data;
  }
};

// ============================================================================
// CV API
// ============================================================================

export const cvAPI = {
  list: async () => {
    const response = await api.get('/cvs');
    return response.data;
  },

  upload: async (file, onProgress) => {
    const formData = new FormData();
    formData.append('file', file);

    const response = await api.post('/cvs/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      onUploadProgress: (progressEvent) => {
        if (onProgress) {
          const progress = Math.round(
            (progressEvent.loaded * 100) / progressEvent.total
          );
          onProgress(progress);
        }
      }
    });
    return response.data;
  },

  delete: async (cvId) => {
    const response = await api.delete(`/cvs/${cvId}`);
    return response.data;
  }
};

// ============================================================================
// JOB DESCRIPTION API
// ============================================================================

export const jobDescriptionAPI = {
  list: async () => {
    const response = await api.get('/job-descriptions');
    return response.data;
  },

  create: async (jobData) => {
    const response = await api.post('/job-descriptions', jobData, {
      timeout: 120000, // 2 minutes for URL scraping
    });
    return response.data;
  },

  delete: async (jdId) => {
    const response = await api.delete(`/job-descriptions/${jdId}`);
    return response.data;
  }
};

// ============================================================================
// COMPARISON API
// ============================================================================

export const comparisonAPI = {
  list: async () => {
    const response = await api.get('/comparisons');
    return response.data;
  },

  create: async (comparisonData) => {
    const response = await api.post('/comparisons', comparisonData, {
      timeout: 180000, // 3 minutes for comprehensive analysis
    });
    return response.data;
  },

  get: async (comparisonId) => {
    const response = await api.get(`/comparisons/${comparisonId}`);
    return response.data;
  }
};

// ============================================================================
// ANALYTICS API
// ============================================================================

export const analyticsAPI = {
  track: async (eventData) => {
    try {
      await api.post('/analytics/track', eventData);
    } catch (error) {
      // Don't throw analytics errors to avoid disrupting user experience
      console.warn('Analytics tracking failed:', error);
    }
  }
};

// ============================================================================
// ADMIN API
// ============================================================================

export const adminAPI = {
  getDashboard: async () => {
    const response = await api.get('/admin/dashboard');
    return response.data;
  },

  getUsers: async () => {
    const response = await api.get('/admin/users');
    return response.data;
  }
};

export default api;