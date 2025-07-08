// frontend/src/components/LogoCustomerCollection/hooks/useLogoCustomerCollectionProgress.js
import { useState } from 'react';
import { fetchLogoData } from '../api/logo_customer_collection';

/**
 * Logo DB’den canlı veri senkronunu tetikler.
 * Senkron bittiğinde true döner (200 OK) – Container yeniden özet veriyi çeker.
 */
const useLogoCustomerCollectionProgress = () => {
  const [loading, setLoading]   = useState(false);
  const [message, setMessage]   = useState('');
  const [error,   setError]     = useState(null);

  const triggerDataRefresh = async () => {
    setLoading(true);
    setError(null);
    setMessage('');
    try {
      const res = await fetchLogoData();          // /backend/.../fetch-logo-data/
      setMessage(res.message || 'Veri güncellendi');
      return true;                                //  ⬅️ container için sinyal
    } catch (e) {
      console.error(e);
      setError('Canlı veri alınamadı');
      return false;
    } finally {
      setLoading(false);
    }
  };

  return { loading, message, error, triggerDataRefresh };
};

export default useLogoCustomerCollectionProgress;
