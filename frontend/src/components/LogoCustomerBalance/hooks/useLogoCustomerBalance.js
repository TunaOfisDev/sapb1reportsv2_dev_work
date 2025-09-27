// frontend/src/components/LogoCustomerBalance/hooks/useLogoCustomerBalance.js
import { useState, useEffect, useCallback } from 'react';
import logocustomerbalance from '../../../api/logocustomerbalance';

const useLogoCustomerBalance = () => {
  const [balances, setBalances] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [updateLoading, setUpdateLoading] = useState(false);

  const fetchBalances = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await logocustomerbalance.fetchCustomerBalances();
      setBalances(data);
    } catch (error) {
      setError('Müşteri bakiyeleri alınırken bir hata oluştu.');
      console.error('Customer Balance Fetching Error:', error);
    } finally {
      setLoading(false);
    }
  }, []);

  const updateBalances = async () => {
    setUpdateLoading(true);
    setError(null);
    try {
      await logocustomerbalance.fetchLogoData();
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

export default useLogoCustomerBalance;
