import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import useAuth from '../../auth/useAuth';
import LoginToast from './LoginToast';
import './LoginForm.css';

function LoginForm() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const { login, isAuthenticated, error, loading } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    if (isAuthenticated) {
      navigate('/');
    }
  }, [isAuthenticated, navigate]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const success = await login(email, password);
      if (success) {
        LoginToast.success();
      } else {
        LoginToast.invalidCredentials();
      }
    } catch (err) {
      console.error('Login error:', err);
      LoginToast.unexpectedError();
    }
  };

  return (
    <div className="login-page-container">
      <div className="login-container">
        <div className="login-area">
          <form onSubmit={handleSubmit} className="login-form">
            <div className="login-form__group">
              <label htmlFor="email" className="login-form__label">Kullanıcı Adı:</label>
              <input
                type="text"
                className="login-form__input"
                id="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                disabled={loading}
              />
            </div>
            <div className="login-form__group">
              <label htmlFor="password" className="login-form__label">Şifre:</label>
              <input
                type="password"
                className="login-form__input"
                id="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                disabled={loading}
              />
            </div>
            {error && <div className="login-form__error">{error}</div>}
            <button type="submit" className="login-form__button" disabled={loading}>
              {loading ? 'Giriş Yapılıyor...' : 'Giriş Yap'}
            </button>
          </form>
        </div>
        <div className="login-footer">
          @Tuna Ofis A.Ş. 2024 - Hana Rapor Uygulaması, Tuna Ofis A.Ş. IT departmanı tarafından ChatGPT teknolojisi kullanılarak geliştirilmiştir. 
          Tüm hakları saklıdır.
        </div>
      </div>
    </div>
  );
}

export default LoginForm;
