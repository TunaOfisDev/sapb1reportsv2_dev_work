// frontend/src/components/logo_supplier_receivables_aging/hooks/useLogoSupplierReceivablesAgingProgress.js

import { useState } from 'react';
import { fetchHanaData } from '../api/logo_supplier_receivables_aging';

/**
 * Veriyi HANA'dan çekip işlem sürecini yöneten hook.
 */
const useLogoSupplierReceivablesAgingProgress = () => {
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');
  const [error, setError] = useState(null);

  const triggerDataRefresh = async () => {
    setLoading(true);
    setError(null);
    setMessage('');

    try {
      const response = await fetchHanaData();
      setMessage(response.message || 'Veri başarıyla güncellendi.');
    } catch (err) {
      setError('Veri alınırken bir hata oluştu.');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return {
    loading,
    message,
    error,
    triggerDataRefresh
  };
};

export default useLogoSupplierReceivablesAgingProgress;
