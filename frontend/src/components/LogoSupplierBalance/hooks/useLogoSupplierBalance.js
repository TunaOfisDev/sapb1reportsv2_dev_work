// frontend/src/components/LogoSupplierBalance/hooks/useLogoSupplierBalance.js
import { useState, useEffect, useCallback } from 'react';
import logosupplierbalance from '../../../api/logosupplierbalance';

const useLogoSupplierBalance = () => {
  const [balances, setBalances] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [updateLoading, setUpdateLoading] = useState(false);

  const fetchBalances = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await logosupplierbalance.fetchSupplierBalances();
      setBalances(data);
    } catch (error) {
      setError('Müşteri bakiyeleri alınırken bir hata oluştu.');
      console.error('Supplier Balance Fetching Error:', error);
    } finally {
      setLoading(false);
    }
  }, []);

  const updateBalances = async () => {
    setUpdateLoading(true);
    setError(null);
    try {
      await logosupplierbalance.fetchLogoData();
      await fetchBalances();  // Güncellemeden sonra verileri tekrar çek
    } catch (error) {
      setError('Veriler güncellenirken bir hata oluştu.');
      console.error('Fetch LOGO Data Error:', error);
    } finally {
      setUpdateLoading(false);
    }
  };

  useEffect(() => {
    fetchBalances();
  }, [fetchBalances]);

  return { balances, loading, error, updateBalances, updateLoading };
};

export default useLogoSupplierBalance;
