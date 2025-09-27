// frontend/src/components/PrivateRoute/PrivateRoute.js
import React from 'react';
import { Navigate } from 'react-router-dom';
import useAuth from '../../auth/useAuth';

const PrivateRoute = ({ children }) => {
  const { isAuthenticated } = useAuth();
  return isAuthenticated ? children : <Navigate to="/login" />;
};

export default PrivateRoute;
