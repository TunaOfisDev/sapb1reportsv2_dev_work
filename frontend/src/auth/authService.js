// frontend/src/auth/authService.js
import axiosInstance from '../api/axiosconfig';
import tokenService from './tokenService';

const ERROR_MESSAGES = {
  LOGIN_FAILED: 'Giriş başarısız. Geçersiz kullanıcı adı veya şifre.',
  SERVER_ERROR: 'Sunucu hatası. Lütfen daha sonra tekrar deneyin.',
  NETWORK_ERROR: 'Ağ hatası. Lütfen internet bağlantınızı kontrol edin.',
  TOKEN_VALIDATION_FAILED: 'Oturum doğrulanamadı. Lütfen tekrar giriş yapın.',
  TOKEN_REFRESH_FAILED: 'Oturum yenilenemedi. Lütfen tekrar giriş yapın.',
};

const login = async (email, password) => {
  try {
    const response = await axiosInstance.post('authcentral/login/', { email, password });
    if (response.data.access && response.data.refresh) {
      tokenService.setUser({
        access: response.data.access,
        refresh: response.data.refresh,
        email: email
      });
      return response.data;
    } else {
      throw new Error(ERROR_MESSAGES.LOGIN_FAILED);
    }
  } catch (error) {
    if (error.response) {
      throw new Error(error.response.data.error || ERROR_MESSAGES.LOGIN_FAILED);
    } else if (error.request) {
      throw new Error(ERROR_MESSAGES.NETWORK_ERROR);
    } else {
      throw new Error(ERROR_MESSAGES.SERVER_ERROR);
    }
  }
};

const validateToken = async () => {
  const accessToken = tokenService.getLocalAccessToken();
  if (!accessToken) {
    logout();
    return false;
  }
  try {
    const response = await axiosInstance.post('authcentral/token/validate/', {
      token: accessToken,
    }, {
      headers: { Authorization: `Bearer ${accessToken}` },
    });
    return response.status === 200;
  } catch (error) {
    console.error('Token validation error:', error);
    logout();
    throw new Error(ERROR_MESSAGES.TOKEN_VALIDATION_FAILED);
  }
};

const refreshToken = async () => {
  const refresh = tokenService.getLocalRefreshToken();
  if (!refresh || tokenService.isTokenExpired(refresh)) {
    logout();
    return false;
  }
  if (!tokenService.shouldRefreshToken(refresh)) {
    return true;
  }
  try {
    const response = await axiosInstance.post('authcentral/token/refresh/', { refresh });
    if (response.data.access) {
      tokenService.updateLocalAccessToken(response.data.access, response.data.refresh);
      return true;
    }
  } catch (error) {
    console.error('Token refresh error:', error);
    logout();
    throw new Error(ERROR_MESSAGES.TOKEN_REFRESH_FAILED);
  }
};

const logout = () => {
  tokenService.removeUser();
  localStorage.clear();
  sessionStorage.clear();
};

const getUserEmail = () => {
  const user = tokenService.getUser();
  return user ? user.email : null;
};

const getUserDepartmentsAndPositions = async () => {
  const accessToken = tokenService.getLocalAccessToken();
  try {
    const response = await axiosInstance.get('authcentral/user/departments_positions/', {
      headers: { Authorization: `Bearer ${accessToken}` },
    });
    return response.data;
  } catch (error) {
    console.error('Error fetching user departments and positions:', error);
    return null;
  }
};

const getCurrentUser = async () => {
  const email = getUserEmail();
  if (!email) {
    return null;
  }
  const departmentsPositions = await getUserDepartmentsAndPositions();
  return {
    email,
    departments: departmentsPositions ? departmentsPositions.departments : [],
    positions: departmentsPositions ? departmentsPositions.positions : []
  };
};

const authService = {
  login,
  validateToken,
  refreshToken,
  logout,
  getUserEmail,
  getUserDepartmentsAndPositions,
  getCurrentUser,
};

export default authService;
