// frontend/src/components/DeliveryDocSum/hooks/useDeliveryDocSum.js
import { useState, useEffect, useCallback } from 'react';
import { fetchSummaryList, fetchHanaData } from '../../../api/deliverydocsum';

/**
 * Sevkiyat özet verisini yönetir:
 *  1. Yerel (PostgreSQL) veriyi çeker.
 *  2. “HANA Veri Çek” tetiklendiğinde arka plandaki job tamamlanana kadar
 *     1 sn aralıklarla kontrol eder (maks. 15 sn).
 *  3. Yenilenmiş veriyi tabloya yansıtır; zaman aşımında uyarı verir.
 */
const useDeliveryDocSum = () => {
  /* ---------- STATE ---------- */
  const [data, setData]           = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError]         = useState(null);
  const [lastUpdated, setLastUpdated] = useState('');

  /* ---------- HELPERS ---------- */

  /** Yerel veriyi getirip state’i günceller */
  const loadLocalData = useCallback(async () => {
    setIsLoading(true);
    try {
      const local = await fetchSummaryList();
      if (local?.length) setLastUpdated(local[0].updated_at);
      setData(local);
      setError(null);
    } catch (err) {
      setError(err.message || 'Yerel veriyi çekerken hata oluştu.');
    } finally {
      setIsLoading(false);
    }
  }, []);

  /** HANA’dan veri çeker ve polling ile sonucu bekler */
  const fetchHana = useCallback(async () => {
    setIsLoading(true);
    setError(null);

    try {
      /* 1) HANA job’ını tetikle */
      const resp = await fetchHanaData();
      if (!resp?.success) {
        throw new Error(resp?.message || 'HANA verisi tetiklenemedi.');
      }

      /* 2) Mevcut zaman damgasını kaydet */
      const prevStamp = lastUpdated;

      /* 3) Polling – her 1 sn’de bir kontrol, maks. 15 deneme (≈15 sn) */
      const MAX_TRIES = 15;
      let tries = 0;
      let updated = false;

      while (tries < MAX_TRIES && !updated) {
        await new Promise(r => setTimeout(r, 1000));
        const fresh = await fetchSummaryList();
        const newStamp = fresh?.[0]?.updated_at;

        if (newStamp && newStamp !== prevStamp) {
          // Yeni veri geldi → state’i güncelle
          setLastUpdated(newStamp);
          setData(fresh);
          updated = true;
        }

        tries += 1;
      }

      if (!updated) {
        setError('HANA verisi 15 sn içinde hazır olmadı (zaman aşımı).');
      }
    } catch (err) {
      setError(err.message || 'HANA verisi çekilirken beklenmedik hata.');
    } finally {
      setIsLoading(false);
    }
  }, [lastUpdated]);

  /* ---------- EFFECTS ---------- */

  /* Sayfa ilk açıldığında yerel veriyi getir */
  useEffect(() => {
    loadLocalData();
  }, [loadLocalData]);

  /* ---------- EXPORT ---------- */
  return {
    data,
    isLoading,
    error,
    lastUpdated,
    loadLocalData,
    fetchHana,
  };
};

export default useDeliveryDocSum;
