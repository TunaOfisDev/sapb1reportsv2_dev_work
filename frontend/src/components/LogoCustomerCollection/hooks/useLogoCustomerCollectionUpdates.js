// frontend/src/components/LogoCustomerCollection/hooks/useLogoCustomerCollectionUpdates.js
import { useState, useEffect } from 'react';
import { fetchLastUpdated } from '../api/logo_customer_collection';

/**
 * Müşteri yaşlandırma verisi için en son güncelleme zamanını çeker.
 * Kullanılacak alan: "lastUpdated"
 */
const useLogoCustomerCollectionUpdates = () => {
  const [lastUpdated, setLastUpdated] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const loadLastUpdated = async () => {
      try {
        const data = await fetchLastUpdated();
        setLastUpdated(data.lastUpdated || null);  // ✅ SADECE lastUpdated
      } catch (err) {
        console.error('Güncelleme zamanı alınamadı:', err);
        setError(err);
      } finally {
        setLoading(false);
      }
    };

    loadLastUpdated();
  }, []);

  return { lastUpdated, loading, error };
};

export default useLogoCustomerCollectionUpdates;
