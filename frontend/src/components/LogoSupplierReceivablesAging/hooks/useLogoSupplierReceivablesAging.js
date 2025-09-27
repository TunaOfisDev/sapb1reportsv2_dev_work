// frontend/src/components/LogoSupplierReceivablesAging/hooks/useLogoSupplierReceivablesAging.js
import { useEffect, useState, useCallback, useMemo } from 'react';
import {
  fetchSupplierAgingSummary,
  fetchHanaData,
  fetchLastUpdated,
} from '../api/logo_supplier_receivables_aging';

const useLogoSupplierReceivablesAging = () => {
  const [data,        setData]        = useState([]);
  const [loading,     setLoading]     = useState(false);
  const [error,       setError]       = useState(null);
  const [lastUpdated, setLastUpdated] = useState(null);

  /** Yerel Postgres özeti + zaman bilgisini birlikte getirir */
  const fetchLocalSummary = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      /** Tablo ve zaman isteğini paralel yürütüyoruz  */
      const [summary, info] = await Promise.all([
        fetchSupplierAgingSummary(),
        fetchLastUpdated(),
      ]);
      setData(summary);
      setLastUpdated(info?.last_updated ?? null);
    } catch (err) {
      console.error('Yerel veri çekme hatası:', err);
      setError('Veri çekilirken bir hata oluştu.');
    } finally {
      setLoading(false);
    }
  }, []);

  /** HANA’dan canlı veri → hazır olunca yeniden özet çek */
  const fetchLiveSummary = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      await fetchHanaData();     // HANA tetikleniyor
      await fetchLocalSummary(); // işlem bitince son durumu çek
      return true;
    } catch (err) {
      console.error('Canlı veri çekme hatası:', err);
      setError('Canlı veri alınırken hata oluştu.');
      return false;
    } finally {
      setLoading(false);
    }
  }, [fetchLocalSummary]);

  /** Negatif bakiye filtrelenmiş görünüm (değişmedi) */
  const filteredData = useMemo(
    () => data.filter(r => parseFloat(r.guncel_bakiye) < 0),
    [data]
  );

  /** İlk açılışta tablo + zaman verisini çek */
  useEffect(() => {
    fetchLocalSummary();
  }, [fetchLocalSummary]);

  return {
    data,
    filteredData,
    loading,
    error,
    lastUpdated,
    fetchLocalSummary, // “Yerel Veri” butonu
    fetchLiveSummary,  // “Anlık Veri” butonu
  };
};

export default useLogoSupplierReceivablesAging;

