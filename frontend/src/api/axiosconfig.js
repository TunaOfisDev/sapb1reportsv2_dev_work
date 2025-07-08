// frontend/src/api/axiosconfig.js
import axios from 'axios';
import authService from '../auth/authService';
import tokenService from '../auth/tokenService';

// API'nin versiyonu ve base URL'si belirleniyor.
const API_VERSION = 'v2';
// eslint-disable-next-line no-undef
const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || `http://${process.env.REACT_APP_SERVER_HOST}/api/${API_VERSION}/`;

// Axios instance'ı oluşturuluyor.
const axiosInstance = axios.create({
  baseURL: API_BASE_URL,
  timeout: 600000, // 600 saniye olarak zaman aşımı süresini tanımlayın (10 dakika)
  headers: {
    'Content-Type': 'application/json;charset=UTF-8',
    'Accept': 'application/json',
    'Accept-Language': 'tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7' // Türkçe dil desteği
  },
  // URL'deki Türkçe karakterlerin doğru encode edilmesi için
  paramsSerializer: params => {
    const searchParams = new URLSearchParams();
    for (const key in params) {
      if (params[key] !== undefined && params[key] !== null) {
        searchParams.append(key, params[key]);
      }
    }
    return searchParams.toString();
  }
});

// İstek göndermeden önce yakalayıcı ile her isteğe otomatik olarak Authorization header ekleniyor.
axiosInstance.interceptors.request.use(
  config => {
    const token = tokenService.getLocalAccessToken();
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`;
    }

    // URL parametrelerinde Türkçe karakter kontrolü
    if (config.params) {
      Object.keys(config.params).forEach(key => {
        if (typeof config.params[key] === 'string') {
          // URL'de Türkçe karakterleri koruyarak encode et
          config.params[key] = encodeURIComponent(config.params[key]);
        }
      });
    }

    return config;
  },
  error => {
    return Promise.reject(error);
  }
);

// Yanıt yakalayıcı ile 401 Unauthorized hatası durumunda token yenileme işlemi yapılıyor.
axiosInstance.interceptors.response.use(
  response => {
    // Yanıtta Türkçe karakter varsa decode et
    if (response.data && typeof response.data === 'string') {
      try {
        response.data = decodeURIComponent(response.data);
      } catch (e) {
        console.warn('Türkçe karakter decode hatası:', e);
      }
    }
    return response;
  },
  async error => {
    const originalRequest = error.config;
    // 401 hatası ve önceden retry yapılmamışsa token yenileme işlemi gerçekleştiriliyor.
    if (error.response && error.response.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      try {
        const refreshTokenSuccess = await authService.refreshToken();
        if (refreshTokenSuccess) {
          originalRequest.headers['Authorization'] = `Bearer ${tokenService.getLocalAccessToken()}`;
          return axiosInstance(originalRequest);
        }
      } catch (error) {
        console.error('Refresh token failed:', error);
        authService.logout();
        window.location.href = '/login';
        return Promise.reject(error);
      }
    }
    // Diğer hatalar için error döndürülüyor.
    return Promise.reject(error);
  }
);

// Global hata yakalayıcı
axiosInstance.interceptors.response.use(
  response => response,
  error => {
    // API yanıtlarındaki Türkçe karakter hatalarını yakala
    if (error.response && error.response.data) {
      console.error('API Hatası:', {
        status: error.response.status,
        data: error.response.data,
        config: {
          url: error.config.url,
          method: error.config.method,
          params: error.config.params
        }
      });
    }
    return Promise.reject(error);
  }
);
axiosInstance.interceptors.response.use(
  response => response,
  error => {
    console.error('API Hatası:', {
      status: error?.response?.status,
      data: error?.response?.data,
      message: error.message,
      config: error?.config
    });
    return Promise.reject(error);
  }
);

export default axiosInstance;