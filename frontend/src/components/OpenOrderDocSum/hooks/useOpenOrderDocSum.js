// frontend/src/components/OpenOrderDocSum/hooks/useOpenOrderDocSum.js
import { useState, useEffect, useCallback } from 'react';
import openOrderDocSumApi from '../../../api/openorderdocsum';

const useOpenOrderDocSum = () => {
  const [openOrderDetails, setOpenOrderDetails] = useState([]);
  const [hanaData, setHanaData] = useState([]);
  const [documentSummaries, setDocumentSummaries] = useState([]);
  const [filteredDocSums, setFilteredDocSums] = useState([]);  // Filtrelenmiş belge özetleri için yeni state
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [lastUpdated, setLastUpdated] = useState('');

  const fetchOpenOrderDetails = useCallback(async () => {
    setLoading(true);
    try {
      const data = await openOrderDocSumApi.fetchOpenOrderDetails();
      setOpenOrderDetails(data);
    } catch (err) {
      setError(err);
    } finally {
      setLoading(false);
    }
  }, []);

  const fetchHanaData = useCallback(async () => {
    setLoading(true);
    try {
      const data = await openOrderDocSumApi.fetchHanaData();
      setHanaData(data);
      // HANA'dan çekilen veri başarılı olduktan sonra son güncellenme zamanını ayarla
      setLastUpdated(formatDate(new Date().toISOString())); // Şimdiki zamanı ISO string olarak al ve formatla
    } catch (err) {
      setError(err);
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
      const data = await openOrderDocSumApi.fetchDocumentSummaries();
      setDocumentSummaries(data);
      // En son güncellenme zamanını alıp formatlayarak güncelle
      if (data.length > 0) {
        setLastUpdated(formatDate(data[0].updated_at));
      }
    } catch (err) {
      setError(err);
    } finally {
      setLoading(false);
    }
  }, []);

  const fetchFilteredDateDocSum = useCallback(async (filters) => {
    setLoading(true);
    try {
      const data = await openOrderDocSumApi.fetchFilteredDateDocSum(filters);
      setFilteredDocSums(data);  // Filtrelenmiş belge özetlerini state'e ata
    } catch (err) {
      setError(err);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchDocumentSummaries();
  }, [fetchDocumentSummaries]);

  return {
    lastUpdated,
    openOrderDetails,
    hanaData,
    documentSummaries,
    filteredDocSums,  // Filtrelenmiş belge özetleri state'ini döndür
    loading,
    error,
    fetchOpenOrderDetails,
    fetchHanaData,
    fetchDocumentSummaries,
    fetchFilteredDateDocSum,  // Filtreleme fonksiyonunu dışa aktar
  };
};

export default useOpenOrderDocSum;

