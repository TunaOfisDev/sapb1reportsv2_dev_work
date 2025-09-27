// frontend/src/components/LoginForm/LoginToast.js
import { toast } from 'react-toastify';

const defaultToastConfig = {
  position: "top-right",
  autoClose: 5000,
  hideProgressBar: false,
  closeOnClick: true,
  pauseOnHover: true,
  draggable: true,
};

const createToast = (type, message, config = {}) => {
  toast[type](message, { ...defaultToastConfig, ...config });
};

const LoginToast = {
  success: (message = 'Giriş başarılı!') => {
    createToast('success', message, { autoClose: 3000 });
  },
  error: (message) => {
    createToast('error', message);
  },
  info: (message) => {
    createToast('info', message, { autoClose: 3000 });
  },
  invalidCredentials: () => {
    LoginToast.error('Geçersiz kullanıcı adı veya şifre.');
  },
  serverError: () => {
    LoginToast.error('Sunucu hatası. Lütfen daha sonra tekrar deneyin.');
  },
  networkError: () => {
    LoginToast.error('Ağ hatası. Lütfen internet bağlantınızı kontrol edin.');
  },
  unexpectedError: () => {
    LoginToast.error('Beklenmeyen bir hata oluştu. Lütfen tekrar deneyin.');
  },
  tokenExpired: () => {
    LoginToast.error('Oturum süresi doldu. Lütfen tekrar giriş yapın.');
  },
  logoutSuccess: () => {
    LoginToast.info('Başarıyla çıkış yapıldı.');
  },
  sessionTimeout: () => {
    LoginToast.error('Oturum zaman aşımına uğradı. Lütfen tekrar giriş yapın.');
  }
};

export default LoginToast;