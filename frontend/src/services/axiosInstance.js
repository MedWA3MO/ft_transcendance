'use client';
import axios from 'axios';

const baseUrl = process.env.NEXT_PUBLIC_URL;

const axiosInstance = axios.create({
  baseURL: `${baseUrl}/backend`,
  timeout: 5000,
  withCredentials: true,
  headers: {
    'Content-Type': 'application/json'
  }
});

// Request interceptor
axiosInstance.interceptors.request.use(
  config => {
    config.url = config.url.replace(/([^:]\/)\/+/g, "$1");

    if (config.data instanceof FormData) {
      delete config.headers['Content-Type'];
    }

    if (config.url.includes('auth/callback')) {
      config.headers = {
        ...config.headers,
        'Cache-Control': 'no-cache, no-store, must-revalidate',
        'Pragma': 'no-cache',
        'Expires': '0'
      };
    }
    return config;
  },
  error => Promise.reject(error)
);

// Response interceptor with error handling and retry logic
let isRetrying = false;

axiosInstance.interceptors.response.use(
  response => response,
  async error => {
    const originalRequest = error.config;

    // Handle 401 Unauthorized
    if (error.response?.status === 401 && !isRetrying) {
      isRetrying = true;
      if (typeof window !== 'undefined' && window.location.pathname !== '/login') {
        window.location.replace('/login');
      }
      isRetrying = false;
      return Promise.reject(error);
    }

    // Retry logic for 500+ errors
    if (
      !originalRequest._retry &&
      originalRequest.method === 'get' &&
      !originalRequest.url.includes('auth/callback') &&
      error.response?.status >= 500
    ) {
      originalRequest._retry = true;
      try {
        return await axiosInstance(originalRequest);
      } catch (retryError) {
        return Promise.reject(retryError);
      }
    }

    return Promise.reject({
      ...error,
      message: error.response?.data?.Error || error.message
    });
  }
);

export default axiosInstance;