// frontend/src/auth/AuthProvider.js tamamlanmış hali
import React, { useState, useEffect, useCallback } from 'react';
import AuthContext from './AuthContext';
import tokenService from './tokenService';
import authService from './authService';

const AuthProvider = ({ children }) => {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [user, setUser] = useState(null);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const initializeAuth = async () => {
      setLoading(true);
      const userData = tokenService.getUser();
      if (userData && userData.access) {
        try {
          const valid = await authService.validateToken();
          if (valid) {
            setIsAuthenticated(true);
            setUser(userData);
          } else {
            throw new Error('Token geçersiz');
          }
        } catch (error) {
          console.error('Token doğrulama hatası:', error);
          setIsAuthenticated(false);
          setUser(null);
          setError('Oturumunuzun süresi dolmuş olabilir. Lütfen tekrar giriş yapın.');
          tokenService.removeUser();
        }
      } else {
        setIsAuthenticated(false);
        setUser(null);
      }
      setLoading(false);
    };
    initializeAuth();
  }, []);

  const login = useCallback(async (email, password) => {
    setLoading(true);
    setError(null);
    try {
      const userData = await authService.login(email, password);
      setIsAuthenticated(true);
      setUser(userData);
      return true;
    } catch (error) {
      console.error('Login hatası:', error);
      setIsAuthenticated(false);
      setUser(null);
      setError(error.message);
      return false;
    } finally {
      setLoading(false);
    }
  }, []);

  const logout = useCallback(() => {
    authService.logout();
    setIsAuthenticated(false);
    setUser(null);
    setError(null);
    return '/login';
  }, []);

  return (
    <AuthContext.Provider value={{ isAuthenticated, user, login, logout, error, loading }}>
      {children}
    </AuthContext.Provider>
  );
};

export default AuthProvider;