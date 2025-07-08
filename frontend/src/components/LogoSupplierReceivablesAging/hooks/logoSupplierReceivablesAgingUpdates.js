
// frontend/src/components/logo_supplier_receivables_aging/hooks/logoSupplierReceivablesAgingUpdates.js

import { useState, useEffect } from 'react';
import { fetchLastUpdated } from '../api/logo_supplier_receivables_aging';

/**
 * Son güncelleme tarihini getiren hook.
 */
const useLogoSupplierReceivablesAgingUpdates = () => {
  const [lastUpdated, setLastUpdated] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const loadLastUpdated = async () => {
      try {
        const data = await fetchLastUpdated();
        setLastUpdated(data.last_updated);
      } catch (err) {
        setError(err);
      } finally {
        setLoading(false);
      }
    };

    loadLastUpdated();
  }, []);

  return { lastUpdated, loading, error };
};

export default useLogoSupplierReceivablesAgingUpdates;
