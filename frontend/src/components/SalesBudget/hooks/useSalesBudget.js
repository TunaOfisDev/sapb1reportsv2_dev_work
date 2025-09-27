// frontend/src/components/SalesBudget/hooks/useSalesBudget.js
import { useState, useEffect, useCallback } from 'react';
import salesBudgetApi from '../../../api/salesbudget';

const useSalesBudget = () => {
  const [salesBudgets, setSalesBudgets] = useState([]);
  const [hanaSalesBudgetData, setHanaSalesBudgetData] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const fetchSalesBudgets = useCallback(async () => {
    setLoading(true);
    setError(null);  // Clear previous errors
    try {
      const data = await salesBudgetApi.getSalesBudgets();
      setSalesBudgets(data);
      setError(null); // Ensure error is cleared on success
    } catch (err) {
      setError(err);
      setSalesBudgets([]);  // Optionally clear data on error
    } finally {
      setLoading(false);
    }
  }, []);

  const fetchHanaSalesBudgetData = useCallback(async () => {
    setLoading(true);
    setError(null);  // Clear previous errors
    try {
      const data = await salesBudgetApi.fetchHanaSalesBudgetData();
      setHanaSalesBudgetData(data);
      setError(null); // Ensure error is cleared on success
    } catch (err) {
      setError(err);
      setHanaSalesBudgetData([]);  // Optionally clear data on error
    } finally {
      setLoading(false);
    }
  }, []);

  const exportSalesBudgetToXLSX = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      await salesBudgetApi.exportSalesBudgetToXLSX();
    } catch (err) {
      setError(err);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchSalesBudgets();
  }, [fetchSalesBudgets]);

  return {
    salesBudgets,
    hanaSalesBudgetData,
    loading,
    error,
    fetchSalesBudgets,
    fetchHanaSalesBudgetData,
    exportSalesBudgetToXLSX,
  };
};

export default useSalesBudget;


