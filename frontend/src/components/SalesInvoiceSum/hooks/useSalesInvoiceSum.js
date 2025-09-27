// frontend/src/components/SalesInvoiceSum/hooks/useSalesInvoiceSum.js
import { useState, useEffect, useCallback } from 'react';
import {
  fetchSummaryList,
  fetchHanaData,
  fetchDynamicNameColumns
} from '../../../api/salesinvoicesum';

const useSalesInvoiceSum = () => {
  /* ---------- STATE ---------- */
  const [data, setData] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [lastUpdated, setLastUpdated] = useState('');
  const [isHanaButtonDisabled, setIsHanaButtonDisabled] = useState(false);

  const [columnNames, setColumnNames] = useState({
    today: 'Bugün',
    yesterday: 'Dün',
    dayBeforeYesterday: 'Önceki Gün',
    threeDaysAgo: 'Bugün-3Gün',
    fourDaysAgo: 'Bugün-4Gün',
    weeklyTotal: 'Hafta',
    thisMonth: 'Bu Ay',
    lastMonth: 'Geçen Ay',
    thisYear: 'Yıllık'
  });

  /* ---------- HELPERS ---------- */
  const loadLocalData = useCallback(async () => {
    setIsLoading(true);
    try {
      const localData = await fetchSummaryList();
      if (localData.length > 0) {
        setLastUpdated(localData[0].updated_at);
      }
      setData([...localData]);       // deep copy – render garantisi
      setError(null);
    } catch (err) {
      setError(err.message || 'Yerel veri çekme hatası.');
    } finally {
      setIsLoading(false);
    }
  }, []);

  const loadDynamicNameColumns = useCallback(async () => {
    try {
      const response = await fetchDynamicNameColumns();
      setColumnNames(response);
    } catch (err) {
      setError(err.message || 'Dinamik kolon isimleri çekme hatası.');
    }
  }, []);

  const refreshData = useCallback(async () => {
    setIsLoading(true);
    try {
      await Promise.all([loadLocalData(), loadDynamicNameColumns()]);
    } finally {
      setIsLoading(false);
    }
  }, [loadLocalData, loadDynamicNameColumns]);

  /* ---------- HANA FETCH ---------- */
const fetchHana = useCallback(
  async () => {
    setIsHanaButtonDisabled(true);
    setIsLoading(true);
    setError(null);

    try {
      const hanaResponse = await fetchHanaData();

      // olası hata durumlarını ayıkla
      if (hanaResponse?.success === false) {
        throw new Error(hanaResponse?.message || 'HANA veri çekme hatası.');
      }
      if (!hanaResponse?.success && !hanaResponse?.message) {
        throw new Error('HANA veri çekme yanıtı geçersiz.');
      }

      /* --- tabloyu hemen boşalt, eski veri görünmesin --- */
      setData([]);

      // polling
      const previousUpdate = lastUpdated;
      let retries = 0;
      const maxRetries = 5;
      const delay = 3000;

      const pollUntilUpdated = async () => {
        try {
          const result = await fetchSummaryList();
          if (result.length > 0 && result[0].updated_at !== previousUpdate) {
            // ✅ Yeni veri geldi
            setLastUpdated(result[0].updated_at);
            setData([...result]);
            await loadDynamicNameColumns();
            setIsLoading(false);
            setIsHanaButtonDisabled(false);   // 🔓 butonu hemen aç
            setError(null);
            return;
          }

          retries += 1;
          if (retries < maxRetries) {
            setTimeout(pollUntilUpdated, delay);
          } else {
            throw new Error('HANA verisi zamanında güncellenmedi.');
          }
        } catch (err) {
          setError(err.message || 'Veri kontrolünde hata oluştu.');
          setIsLoading(false);
          setIsHanaButtonDisabled(false);     // 🔓 hata da olsa butonu aç
        }
      };

      pollUntilUpdated();
    } catch (err) {
      setError(err.message || 'HANA veri çekme işlemi başarısız.');
      setIsLoading(false);
      setIsHanaButtonDisabled(false);         // 🔓 try/catch hatası
    }
  },
  [lastUpdated, loadDynamicNameColumns]
);


  /* ---------- EFFECTS ---------- */
  useEffect(() => {
    refreshData();
  }, [refreshData]);

  /* ---------- RETURN ---------- */
  return {
    data,
    isLoading,
    error,
    fetchHana,
    loadLocalData,
    loadDynamicNameColumns,
    columnNames,
    lastUpdated,
    isHanaButtonDisabled
  };
};

export default useSalesInvoiceSum;
