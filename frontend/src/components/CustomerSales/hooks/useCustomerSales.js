// frontend/src/components/customersales/hooks/useCustomerSales.js
import { useState, useEffect, useCallback } from 'react';
import customersalesApi from '../../../api/customersales';

const useCustomerSales = () => {
  const [customerSalesOrders, setCustomerSalesOrders] = useState([]);
  const [hanaCustomerSalesData, setHanaCustomerSalesData] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [lastUpdated, setLastUpdated] = useState('');

  const fetchCustomerSalesOrders = useCallback(async () => {
    setLoading(true);
    try {
      const data = await customersalesApi.getCustomerSalesOrders();
      setCustomerSalesOrders(data);
    } catch (err) {
      setError(err);
    } finally {
      setLoading(false);
    }
  }, []);

  const fetchHanaCustomerSalesData = useCallback(async () => {
    setLoading(true);
    try {
      const data = await customersalesApi.fetchHanaCustomerSalesData();
      setHanaCustomerSalesData(data);
    } catch (err) {
      setError(err);
    } finally {
      setLoading(false);
    }
  }, []);

  const fetchLastUpdatedTime = useCallback(async () => {
    setLoading(true);
    try {
      const lastUpdatedTime = await customersalesApi.getLastUpdatedTime();
      // API'den dönen veriyi kontrol edin ve uygun şekilde işleyin
      setLastUpdated(lastUpdatedTime); // API'den dönen zaman bilgisini doğrudan atayın
    } catch (err) {
      setError(err);
    } finally {
      setLoading(false);
    }
  }, []);
  

  // Export to XLSX işlemini yapan yeni bir fonksiyon ekliyoruz.
  const exportCustomerSalesToXLSX = useCallback(async () => {
    setLoading(true);
    try {
      await customersalesApi.exportCustomerSalesToXLSX();
    } catch (err) {
      setError(err);
    } finally {
      setLoading(false);
    }
  }, []);

  // useEffect içinde diğer data fetching işlemleri ile birlikte bu fonksiyonu da çağırmak için bir çağrı ekleyin
  useEffect(() => {
    fetchCustomerSalesOrders();
    fetchLastUpdatedTime();
    // Şu anlık bu fonksiyonu burada çağırmıyoruz çünkü bu işlem bir buton veya benzeri bir tetikleyiciyle kullanıcı isteği üzerine yapılmalı.
  }, [fetchCustomerSalesOrders, fetchLastUpdatedTime]);

  // Son olarak, tüm state'leri ve fonksiyonları return ediyoruz.
  return {
    customerSalesOrders,
    hanaCustomerSalesData,
    lastUpdated,
    loading,
    error,
    fetchCustomerSalesOrders,
    fetchHanaCustomerSalesData,
    fetchLastUpdatedTime,
    exportCustomerSalesToXLSX,
  };
};

export default useCustomerSales;
