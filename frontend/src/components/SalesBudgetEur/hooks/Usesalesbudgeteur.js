// frontend/src/components/SalesBudgetEur/hooks/Usesalesbudgeteur.js
import { useState, useEffect, useCallback } from 'react';
import {
  fetchSalesBudgetEUR,
  fetchSalesBudgetFromHana,
  exportSalesBudgetEURToExcel,
} from '../api/salesbudgeteurApi';
import transformRow from '../utils/transformRow';
import { formatDateTime } from '../utils/DateTimeFormat';

export default function useSalesBudgetEUR() {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(false);
  const [exporting, setExporting] = useState(false);
  const [error, setError] = useState(null);
  const [lastUpdated, setLastUpdated] = useState('Bilinmiyor');

  /* ---------- Son güncelleme hesaplama ---------- */
  const deriveLastUpdated = (rawArr) => {
    if (rawArr?.length && rawArr[0].updated_at) {
      return formatDateTime(rawArr[0].updated_at);
    }
    return 'Bilinmiyor';
  };

  /* ---------- Yerel veritabanından veri çek ---------- */
  const loadData = useCallback(async () => {
    setLoading(true);
    setError(null);

    try {
      const raw = await fetchSalesBudgetEUR();
      setData(raw.map(transformRow));
      setLastUpdated(deriveLastUpdated(raw));     // << burada formatlı zamanı kaydet
    } catch (err) {
      setError(err);
      console.error('SalesBudgetEUR yükleme hatası:', err);
    } finally {
      setLoading(false);
    }
  }, []);

  /* ---------- HANA’dan canlı veri çek ---------- */
  const fetchFromHana = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      await fetchSalesBudgetFromHana();
      await loadData();                          // loadData zaten lastUpdated’i yeniler
    } catch (err) {
      setError(err);
      console.error('HANA veri çekme hatası:', err);
    } finally {
      setLoading(false);
    }
  }, [loadData]);

  /* ---------- Excel’e aktar ---------- */
  const exportToExcel = useCallback(async () => {
    setExporting(true);
    setError(null);
    try {
      const response = await exportSalesBudgetEURToExcel();
      const blob = new Blob([response.data], {
        type:
          'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
      });
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', 'salesbudget-eur.xlsx');
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (err) {
      setError(err);
      console.error('Excel export hatası:', err);
    } finally {
      setExporting(false);
    }
  }, []);

  /* ---------- İlk yükleme ---------- */
  useEffect(() => {
    loadData();
  }, [loadData]);

  return {
    data,
    loading,
    exporting,
    error,
    lastUpdated,   // ← biçimlendirilmiş string olarak döner
    reload: loadData,
    fetchFromHana,
    exportToExcel,
  };
}
