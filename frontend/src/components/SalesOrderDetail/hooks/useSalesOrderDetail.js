// frontend/src/components/SalesOrderDetail/hooks/useSalesOrderDetail.js
import { useState, useEffect, useCallback } from 'react';
import salesOrderDetailApi from '../../../api/salesorderdetail';

const useSalesOrderDetail = () => {
  const [salesOrderMasters, setSalesOrderMasters] = useState([]);
  const [hanaSalesOrderData, setHanaSalesOrderData] = useState([]);
  const [salesOrderDetail, setSalesOrderDetail] = useState(null);
  const [modalVisible, setModalVisible] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [lastUpdated, setLastUpdated] = useState('');
  const defaultPageSize = 20;

  const fetchSalesOrderMasters = useCallback(async (page = 1, pageSize = defaultPageSize) => {
    setLoading(true);
    try {
      const response = await salesOrderDetailApi.fetchSalesOrderMasters(page, pageSize);
      setSalesOrderMasters(response.results);
    } catch (err) {
      setError('Sales order masters çekilirken bir hata oluştu: ' + err.message);
    } finally {
      setLoading(false);
    }
  }, [defaultPageSize]);

  const fetchHanaSalesOrderData = useCallback(async () => {
    setLoading(true);
    try {
      const response = await salesOrderDetailApi.fetchHanaSalesOrderData();
      setHanaSalesOrderData(response);
      setLastUpdated(new Date().toLocaleString());
    } catch (err) {
      setError('HANA verileri çekilirken bir hata oluştu: ' + err.message);
    } finally {
      setLoading(false);
    }
  }, []);

  const fetchSalesOrderDetailsByMasterBelgeGirisNo = useCallback(async (masterBelgeGirisNo) => {
    setLoading(true);
    try {
      const response = await salesOrderDetailApi.fetchSalesOrderDetailsByMasterBelgeGirisNo(masterBelgeGirisNo);
      setSalesOrderDetail(response.results); // Assuming your API returns an object with a 'results' array
      setModalVisible(true);
    } catch (err) {
      setError(`Sales order details for master ID ${masterBelgeGirisNo} could not be fetched: ` + err.message);
    } finally {
      setLoading(false);
    }
  }, []);

  const hideModal = () => setModalVisible(false);

  useEffect(() => {
    fetchSalesOrderMasters();
  }, [fetchSalesOrderMasters]);

  return {
    salesOrderMasters,
    hanaSalesOrderData,
    salesOrderDetail,
    lastUpdated,
    modalVisible,
    loading,
    error,
    fetchSalesOrderMasters,
    fetchHanaSalesOrderData,
    fetchSalesOrderDetailsByMasterBelgeGirisNo,
    hideModal
  };
};

export default useSalesOrderDetail;

