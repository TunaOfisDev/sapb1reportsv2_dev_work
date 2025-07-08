// frontend/src/components/salesorder/hooks/UseSalesOrder.js
import { useState, useCallback } from 'react';
import salesOrderApi from '../../../api/salesorder';

const UseSalesOrder = () => {
  const [localSalesOrder, setLocalSalesOrder] = useState([]);
  const [instantSalesOrder, setInstantSalesOrder] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const fetchLocalSalesOrder = useCallback(async () => {
    setLoading(true);
    try {
      const data = await salesOrderApi.fetchLocalData();
      setLocalSalesOrder(data);
    } catch (err) {
      setError(err);
    } finally {
      setLoading(false);
    }
  }, []);

  const fetchInstantSalesOrder = useCallback(async () => {
    setLoading(true);
    try {
      const data = await salesOrderApi.fetchInstantData();
      setInstantSalesOrder(data);
    } catch (err) {
      setError(err);
    } finally {
      setLoading(false);
    }
  }, []);

  const applyTimeFilter = useCallback(async (startTime, endTime) => {
    setLoading(true);
    try {
      const data = await salesOrderApi.filterSalesOrdersByTime(startTime, endTime);
      setLocalSalesOrder(data); // Veya instantSalesOrder'a uygulanabilir, bağlama göre ayarlayın
    } catch (err) {
      setError(err);
    } finally {
      setLoading(false);
    }
  }, []);

  const applySecondFilter = useCallback(async (filterCriteria) => {
    setLoading(true);
    try {
      const data = await salesOrderApi.filterSalesOrdersBySecondFilter(filterCriteria);
      setLocalSalesOrder(data); // Veya instantSalesOrder'a uygulanabilir, bağlama göre ayarlayın
    } catch (err) {
      setError(err);
    } finally {
      setLoading(false);
    }
  }, []);

  return {
    localSalesOrder,
    instantSalesOrder,
    loading,
    error,
    fetchLocalSalesOrder,
    fetchInstantSalesOrder,
    applyTimeFilter,
    applySecondFilter,
  };
};

export default UseSalesOrder;

