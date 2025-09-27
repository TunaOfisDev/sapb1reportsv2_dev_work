// frontend/src/components/SalesOrderDocSum/hooks/useSalesOrderDocSum.js
import { useState, useEffect, useCallback } from 'react';
import salesOrderDocSumApi from '../../../api/salesorderdocsum';
import Toastify from '../utils/Toastify';

const useSalesOrderDocSum = () => {
  const [salesOrderDetails, setSalesOrderDetails] = useState([]);
  const [hanaData, setHanaData] = useState([]);
  const [documentSummaries, setDocumentSummaries] = useState([]);
  const [filteredDocSums, setFilteredDocSums] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [lastUpdated, setLastUpdated] = useState('');

  const fetchSalesOrderDetails = useCallback(async () => {
    setLoading(true);
    try {
      const data = await salesOrderDocSumApi.fetchSalesOrderDetails();
      setSalesOrderDetails(data);
    } catch (err) {
      setError(err);
      Toastify.error('Satış siparişi detayları alınırken bir hata oluştu');
    } finally {
      setLoading(false);
    }
  }, []);

  const fetchHanaData = useCallback(async () => {
    setLoading(true);
    try {
      Toastify.hanaDataFetch.start();
      const data = await salesOrderDocSumApi.fetchHanaData();
      setHanaData(data);
      setLastUpdated(formatDate(new Date().toISOString()));
      Toastify.hanaDataFetch.success();
    } catch (err) {
      setError(err);
      Toastify.hanaDataFetch.error();
    } finally {
      setLoading(false);
    }
  }, []);

  const fetchSalesOrderDetailByBelgeNo = useCallback(async (belgeNo) => {
    setLoading(true);
    try {
      const data = await salesOrderDocSumApi.fetchSalesOrderDetailByBelgeNo(belgeNo);
      return data;
    } catch (err) {
      setError(err);
      Toastify.error(`${belgeNo} numaralı belge detayları alınırken bir hata oluştu`);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  const formatDate = (isoString) => {
    const date = new Date(isoString);
    const day = date.getDate().toString().padStart(2, '0');
    const month = (date.getMonth() + 1).toString().padStart(2, '0');
    const year = date.getFullYear();
    const hours = date.getHours().toString().padStart(2, '0');
    const minutes = date.getMinutes().toString().padStart(2, '0');
    return `${day}.${month}.${year} ${hours}:${minutes}`;
  };
  
  const fetchDocumentSummaries = useCallback(async () => {
    setLoading(true);
    try {
      const data = await salesOrderDocSumApi.fetchDocumentSummaries();
      setDocumentSummaries(data);
      if (data.length > 0) {
        setLastUpdated(formatDate(data[0].updated_at));
      }
    } catch (err) {
      setError(err);
      Toastify.error('Belge özetleri alınırken bir hata oluştu');
    } finally {
      setLoading(false);
    }
  }, []);

  const fetchFilteredDateDocSum = useCallback(async (filters) => {
    setLoading(true);
    try {
      const data = await salesOrderDocSumApi.fetchFilteredDateDocSum(filters);
      setFilteredDocSums(data);
    } catch (err) {
      setError(err);
      Toastify.error('Filtrelenmiş belge özetleri alınırken bir hata oluştu');
    } finally {
      setLoading(false);
    }
  }, []);

  const fetchHanaDataAndRefresh = useCallback(async () => {
    setLoading(true);
    try {
      Toastify.hanaDataFetchAndRefresh.start();
      const data = await salesOrderDocSumApi.fetchHanaData();
      setHanaData(data);
      setLastUpdated(formatDate(new Date().toISOString()));
      
      // 5 saniye bekle ve ardından tabloyu yenile
      setTimeout(async () => {
        try {
          await fetchDocumentSummaries();
          Toastify.hanaDataFetchAndRefresh.success();
        } catch (err) {
          Toastify.error('Tablo güncellenirken bir hata oluştu');
        }
      }, 5000);
    } catch (err) {
      setError(err);
      Toastify.hanaDataFetchAndRefresh.error();
    } finally {
      setLoading(false);
    }
  }, [fetchDocumentSummaries]);

  useEffect(() => {
    fetchDocumentSummaries();
  }, [fetchDocumentSummaries]);

  return {
    lastUpdated,
    salesOrderDetails,
    hanaData,
    documentSummaries,
    filteredDocSums,
    loading,
    error,
    fetchSalesOrderDetails,
    fetchHanaData,
    fetchSalesOrderDetailByBelgeNo,
    fetchDocumentSummaries,
    fetchFilteredDateDocSum,
    fetchHanaDataAndRefresh,
  };
};

export default useSalesOrderDocSum;
