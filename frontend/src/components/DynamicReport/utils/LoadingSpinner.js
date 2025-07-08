// frontend/src/components/DynamicReport/utils/LoadingSpinner.js
import React from 'react';

const LoadingSpinner = ({ isLoading }) => {
  if (!isLoading) {
    return null;  // Eğer isLoading false ise, hiçbir şey render etme
  }

  return (
    <div className="loading-spinner">
      <div className="spinner-border text-primary" role="status">
        <span className="sr-only">Yükleniyor...</span>
      </div>
    </div>
  );
};

export default LoadingSpinner;
