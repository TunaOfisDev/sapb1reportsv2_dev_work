// path: frontend/src/components/StockCardIntegration/hooks/useApiStatus.js

import { useState, useCallback } from 'react';

/**
 * API çağrılarında loading, success, error gibi durumları merkezi kontrol etmek için hook
 */
const useApiStatus = () => {
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(null);
  const [error, setError] = useState(null);

  const start = useCallback(() => {
    setLoading(true);
    setSuccess(null);
    setError(null);
  }, []);

  const succeed = useCallback((message = null) => {
    setLoading(false);
    setSuccess(message || 'İşlem başarıyla tamamlandı.');
  }, []);

  const fail = useCallback((errorObj) => {
    setLoading(false);
    if (errorObj?.response?.data?.detail) {
      setError(errorObj.response.data.detail);
    } else if (typeof errorObj === 'string') {
      setError(errorObj);
    } else {
      setError('Bir hata oluştu, lütfen tekrar deneyin.');
    }
  }, []);

  const reset = useCallback(() => {
    setLoading(false);
    setSuccess(null);
    setError(null);
  }, []);

  return {
    loading,
    success,
    error,
    start,
    succeed,  // <-- Bu fonksiyon önemli!
    fail,
    reset
  };
};

export default useApiStatus;
