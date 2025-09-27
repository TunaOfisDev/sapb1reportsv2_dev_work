// frontend/src/auth/tokenService.js
import { jwtDecode } from 'jwt-decode';

const setUser = (data) => {
  const userData = {
    access: data.access,
    refresh: data.refresh,
    email: data.email,
  };
  localStorage.setItem('user', JSON.stringify(userData));
};

const getUser = () => {
  return JSON.parse(localStorage.getItem('user'));
};

const removeUser = () => {
  localStorage.removeItem('user');
};

const getLocalAccessToken = () => {
  const user = getUser();
  return user?.access || null;
};

const getLocalRefreshToken = () => {
  const user = getUser();
  return user?.refresh || null;
};

// Token'ın süresinin dolup dolmadığını kontrol eder
const isTokenExpired = (token) => {
  if (!token) return true;
  const decoded = jwtDecode(token);
  const currentTime = Date.now() / 1000;
  return decoded.exp < currentTime;
};

// Token'ı yenileme zamanı gelip gelmediğini kontrol eder
const shouldRefreshToken = (token) => {
  if (!token) return false;
  const decoded = jwtDecode(token);
  const currentTime = Date.now() / 1000;
  return decoded.exp - currentTime < 300;
};

const updateLocalAccessToken = (newAccessToken, newRefreshToken) => {
  const user = getUser();
  if (user) {
    user.access = newAccessToken;
    // Yeni refresh token'ı kontrol et ve varsa güncelle
    if (newRefreshToken) {
      user.refresh = newRefreshToken;
    }
    localStorage.setItem('user', JSON.stringify(user));
  }
};

const tokenService = {
  setUser,
  getUser,
  removeUser,
  getLocalAccessToken,
  getLocalRefreshToken,
  updateLocalAccessToken,
  isTokenExpired,
  shouldRefreshToken,
};

export default tokenService;
