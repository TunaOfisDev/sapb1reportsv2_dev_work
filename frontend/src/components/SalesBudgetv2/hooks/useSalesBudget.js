// frontend/src/components/SalesBudgetv2/hooks/useSalesBudget.js
import { useState, useCallback } from 'react';
import salesbudgetv2 from '../../../api/salesbudgetv2';

const useSalesBudget = () => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const fetchSalesBudgets = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await salesbudgetv2.getsalesbudgetv2s();
      setLoading(false);
      return data;
    } catch (err) {
      console.error('Bütçeleri getirirken hata:', err);
      setError(err.message || 'Bütçeler yüklenirken bir hata oluştu');
      setLoading(false);
      throw err;
    }
  }, []);

  const fetchHanaSalesBudgetData = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await salesbudgetv2.fetchHanasalesbudgetv2Data();
      setLoading(false);
      return data;
    } catch (err) {
      console.error('HANA verilerini getirirken hata:', err);
      setError(err.message || 'HANA verileri yüklenirken bir hata oluştu');
      setLoading(false);
      throw err;
    }
  }, []);

  const exportSalesBudgetToXLSX = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      await salesbudgetv2.exportsalesbudgetv2ToXLSX();
      setLoading(false);
    } catch (err) {
      console.error('Excel\'e aktarma hatası:', err);
      setError(err.message || 'Excel\'e aktarma işlemi başarısız oldu');
      setLoading(false);
      throw err;
    }
  }, []);

  return {
    loading,
    error,
    fetchSalesBudgets,
    fetchHanaSalesBudgetData,
    exportSalesBudgetToXLSX
  };
};

export default useSalesBudget;