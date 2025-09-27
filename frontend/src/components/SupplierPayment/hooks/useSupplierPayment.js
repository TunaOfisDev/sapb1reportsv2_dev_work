// frontend/src/components/SupplierPayment/hooks/useSupplierPayment.js
import { useState, useEffect, useCallback } from 'react';
import supplierPaymentApi from '../../../api/supplierpayment';
import XLSXExport from '../utils/XLSXExport';
import useSupplierPaymentProgress from './useSupplierPaymentProgress';

const useSupplierPayment = () => {
  const [localDbSupplierPayments, setLocalDbSupplierPayments] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [lastUpdated, setLastUpdated] = useState(null);
  const [processedData, setProcessedData] = useState(null);
  const { progress, startTask } = useSupplierPaymentProgress();

  const fetchLastUpdatedTime = useCallback(async () => {
    try {
      const response = await supplierPaymentApi.getLastUpdatedTime();
      console.log('Last Updated Response:', response); // Debug için
      if (response?.last_updated) {
        setLastUpdated(response.last_updated);
        console.log('Setting Last Updated:', response.last_updated); // Debug için
      } else {
        setLastUpdated(''); // API'den veri gelmezse boş string set et
      }
    } catch (err) {
      console.error('Son güncelleme zamanı alınamadı:', err);
      setLastUpdated(''); // Hata durumunda boş string set et
    }
  }, []);

  const fetchLocalDbSupplierPayments = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await supplierPaymentApi.getLocalDbSupplierPayments();
      if (response && Array.isArray(response)) {
        setLocalDbSupplierPayments(response);
        await fetchLastUpdatedTime(); // Son güncelleme zamanını al
      } else {
        throw new Error('Geçersiz veri formatı');
      }
    } catch (err) {
      console.error('Yerel DB verisi çekilirken hata:', err);
      setError(err.response?.data?.message || 'Yerel veritabanından veri çekilemedi.');
    } finally {
      setLoading(false);
    }
  }, [fetchLastUpdatedTime]);

  const fetchHanaDbCombinedService = useCallback(async () => {
    setLoading(true);
    try {
      await startTask();
      await fetchLastUpdatedTime(); // Son güncelleme zamanını al
    } catch (err) {
      setError('HANA verisi çekilirken bir hata oluştu.');
    } finally {
      setLoading(false);
    }
  }, [startTask, fetchLastUpdatedTime]);

  const fetchHanaDbData = useCallback(async () => {
    setLoading(true);
    setError(null);
    setProcessedData(null);
    try {
      const response = await supplierPaymentApi.fetchHanaDb();
      
      if (response.status === 'success') {
        setProcessedData(response.details?.processed || null);
        await fetchLastUpdatedTime(); // Son güncelleme zamanını al
        return true;
      } else if (response.status === 'no_data') {
        setError(response.message);
        return false;
      }
    } catch (err) {
      let errorMessage;
      
      if (err.response) {
        if (err.response.status === 404) {
          errorMessage = err.response.data.message || 'HANA veritabanında yeni veri bulunamadı.';
        } else if (err.response.status === 500) {
          errorMessage = err.response.data.message || 'Sunucu hatası oluştu.';
        } else {
          errorMessage = err.response.data.message || 'Beklenmeyen bir hata oluştu.';
        }
        setProcessedData(err.response.data.details?.processed || null);
      } else if (err.request) {
        errorMessage = 'Sunucuya bağlanılamadı. İnternet bağlantınızı kontrol edin.';
      } else {
        errorMessage = 'Bir hata oluştu. Lütfen tekrar deneyin.';
      }
      
      setError(errorMessage);
      return false;
    } finally {
      setLoading(false);
    }
  }, [fetchLastUpdatedTime]);

  const exportSupplierPaymentsToXLSX = useCallback(() => {
    if (localDbSupplierPayments.length > 0) {
      XLSXExport.exportToExcel(localDbSupplierPayments, 'Tedarikci_Odemeleri');
    }
  }, [localDbSupplierPayments]);

  // Başlangıçta verileri ve son güncelleme zamanını yükle
  useEffect(() => {
    fetchLocalDbSupplierPayments();
    fetchLastUpdatedTime();
  }, [fetchLocalDbSupplierPayments, fetchLastUpdatedTime]);

  return {
    localDbSupplierPayments,
    lastUpdated,
    loading,
    error,
    processedData,
    fetchLocalDbSupplierPayments,
    fetchHanaDbCombinedService,
    fetchHanaDbData,
    fetchLastUpdatedTime,
    exportSupplierPaymentsToXLSX,
    progress
  };
};

export default useSupplierPayment;