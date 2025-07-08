// frontend/src/components/productpicture/utils/LoadingSpinner.js
import React from 'react';
import '../css/LoadingSpinner.css'; // Stil dosyasını import edin

const LoadingSpinner = ({ isLoading }) => {
  if (!isLoading) {
    return null;
  }

return (
    <div className="loading-spinner">
      <div className="spinner-border text-primary" role="status">
      {/* Yükleme mesajı ekleme */}
      <span className="loading-text">Lütfen bekleyin, veriler yükleniyor...</span>
      </div>
      </div>
      );
      };

export default LoadingSpinner;