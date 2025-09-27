// frontend/src/components/SalesOfferDocSum/hooks/usePivotTables.js
import { useState, useEffect, useCallback } from 'react';
import salesOfferDocSumApi from '../../../api/salesofferdocsum';

const usePivotTables = () => {
  const [customerMonthlySummary, setCustomerMonthlySummary] = useState([]);
  const [monthlySummary, setMonthlySummary] = useState([]);
  const [sellerMonthlySummary, setSellerMonthlySummary] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const fetchCustomerMonthlySummary = useCallback(async () => {
    setLoading(true);
    try {
      const data = await salesOfferDocSumApi.fetchCustomerMonthlySummary();
      console.log('Customer Monthly Summary Data:', data); // Debugging amaçlı
      setCustomerMonthlySummary(data);
      setError(null);
    } catch (err) {
      console.error('Error fetching customer monthly summary:', err);
      setError('Customer monthly summary data could not be loaded.');
    } finally {
      setLoading(false);
    }
  }, []);

  const fetchMonthlySummary = useCallback(async () => {
    setLoading(true);
    try {
      const data = await salesOfferDocSumApi.fetchMonthlySummary();
      console.log('Monthly Summary Data:', data); // Debugging amaçlı
      setMonthlySummary(data);
      setError(null);
    } catch (err) {
      console.error('Error fetching monthly summary:', err);
      setError('Monthly summary data could not be loaded.');
    } finally {
      setLoading(false);
    }
  }, []);

  const fetchSellerMonthlySummary = useCallback(async () => {
    setLoading(true);
    try {
      const data = await salesOfferDocSumApi.fetchSellerMonthlySummary();
      console.log('Seller Monthly Summary Data:', data); // Debugging amaçlı
      setSellerMonthlySummary(data);
      setError(null);
    } catch (err) {
      console.error('Error fetching seller monthly summary:', err);
      setError('Seller monthly summary data could not be loaded.');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchCustomerMonthlySummary();
    fetchMonthlySummary();
    fetchSellerMonthlySummary();
  }, [fetchCustomerMonthlySummary, fetchMonthlySummary, fetchSellerMonthlySummary]);

  const refreshData = useCallback(() => {
    fetchCustomerMonthlySummary();
    fetchMonthlySummary();
    fetchSellerMonthlySummary();
  }, [fetchCustomerMonthlySummary, fetchMonthlySummary, fetchSellerMonthlySummary]);

  return {
    customerMonthlySummary,
    monthlySummary,
    sellerMonthlySummary,
    loading,
    error,
    refreshData
  };
};

export default usePivotTables;
