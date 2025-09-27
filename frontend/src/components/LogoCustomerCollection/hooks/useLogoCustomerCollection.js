// frontend/src/components/LogoCustomerCollection/hooks/useLogoCustomerCollection.js
import { useState, useCallback, useEffect, useMemo } from 'react';
import {
  fetchCustomerAgingSummary,
  fetchLogoData,
  fetchLastUpdated,
} from '../api/logo_customer_collection';

const useLogoCustomerCollection = () => {
  /* ---------- state ---------- */
  const [data,        setData]        = useState([]);
  const [loading,     setLoading]     = useState(false);
  const [error,       setError]       = useState(null);
  const [lastUpdated, setLastUpdated] = useState(null);

  /* ---------- yardımcı ---------- */
  const fetchLocalSummary = useCallback(async () => {
    setLoading(true); setError(null);
    try {
      const res = await fetchCustomerAgingSummary();
      setData(res);
    } catch (e) {
      setError('Veri alınırken hata oluştu.');
      console.error(e);
    } finally { setLoading(false); }
  }, []);

  const fetchLastUpdatedData = useCallback(async () => {
    try {
      const info = await fetchLastUpdated();
      setLastUpdated(info.lastUpdated           // ISO string → tercih
                  || info.serverTime            // (geriye dönük)
                  || info.lastPeriod            // "MM-YYYY"
                  || null);
    } catch (e) {
      console.error(e);
      setError('Son güncelleme okunamadı.');
    }
  }, []);

  /* ------------- canlı senkron -------------- */
  const fetchLiveSummary = useCallback(async () => {
    setLoading(true); setError(null);
    try {
      await fetchLogoData();          // Logo DB’den senkron
      // ✔ Senkrondan sonra her iki veriyi de tazele
      await fetchLocalSummary();
      await fetchLastUpdatedData();
      return true;
    } catch (e) {
      setError('Canlı veri alınamadı.');
      console.error(e);
      return false;
    } finally { setLoading(false); }
  }, [fetchLocalSummary, fetchLastUpdatedData]);

  /* ------------- filtreli görünüm ------------- */
  const filteredData = useMemo(
    () => data.filter(r => Number(r.guncel_bakiye) > 0),
    [data],
  );

  /* ------------- mount’ta ilk yük ------------- */
  useEffect(() => {
    (async () => {
      await fetchLocalSummary();
      await fetchLastUpdatedData();
    })();
  }, [fetchLocalSummary, fetchLastUpdatedData]);

  /* ------------- export ------------- */
  return {
    data,
    filteredData,
    loading,
    error,
    lastUpdated,
    fetchLocalSummary,
    fetchLiveSummary,       // artık live işini kendi yapıyor
  };
};

export default useLogoCustomerCollection;
