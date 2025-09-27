// frontend/src/components/TunaInsSupplierPayment/containers/SupplierPaymentContainer.js
import React, { useEffect, useState } from 'react';
import useSupplierPayment from '../hooks/useSupplierPayment';
import SupplierPaymentTable from './SupplierPaymentTable';
import SupplierPaymentUpdates from '../hooks/SupplierPaymentUpdates';
import supplierpaymentAPI from '../../../api/supplierpayment';
import '../css/SupplierPaymentContainer.css';

const TunaInsSupplierPaymentContainer = () => {
  const {
    localDbSupplierPayments,
    lastUpdated,
    loading,
    error,
    fetchLocalDbSupplierPayments,
    fetchHanaDbData,
    fetchLastUpdatedTime,
    exportSupplierPaymentsToXLSX,
    progress,
    processedData
  } = useSupplierPayment();
  
  const [messages, setMessages] = useState([]);

  useEffect(() => {
    const socket = supplierpaymentAPI.createWebSocketConnection((message) => {
      setMessages((prevMessages) => [...prevMessages, message]);
    });

    return () => {
      socket.close();
    };
  }, []);

  useEffect(() => {
    // Bileşen mount olduğunda son güncelleme zamanını al
    fetchLastUpdatedTime();
  }, [fetchLastUpdatedTime]);

  const handleFetchHanaDbData = async () => {
    const success = await fetchHanaDbData();
    if (success) {
      await fetchLocalDbSupplierPayments();
      await fetchLastUpdatedTime();
    }
  };

  return (
    <div className="supplier-payment-container">
      <div className="supplier-payment-container__header">
        <h1 className="supplier-payment-container__title">Tuna Ins Tedarikci Odeme Listesi</h1>
        <div className="supplier-payment-container__last-updated">
          <span>
            {lastUpdated ? `Son Güncellenme: ${lastUpdated}` : 'Son güncelleme bilgisi alınıyor...'}
          </span>
        </div>
        <div className="supplier-payment-container__button-wrapper">
          <button 
            onClick={fetchLocalDbSupplierPayments} 
            className="supplier-payment-container__button"
            disabled={loading}
          >
            Yerel Veri Çek
          </button>
          <button 
            onClick={handleFetchHanaDbData} 
            className="supplier-payment-container__button"
            disabled={loading}
          >
            HANA Anlık Veri Çek
          </button>
          <button 
            onClick={exportSupplierPaymentsToXLSX} 
            className="supplier-payment-container__button"
            disabled={loading || localDbSupplierPayments.length === 0}
          >
            Excel'e Aktar
          </button>
        </div>
      </div>

      {loading && (
        <div className="supplier-payment-container__loading">
          <p>Yükleniyor...</p>
          {progress && <p>{progress}</p>}
        </div>
      )}

      {error && (
        <div className="supplier-payment-container__error">
          <p>{error}</p>
          {lastUpdated && (
            <div className="supplier-payment-container__last-updated-info">
              <span>Son Başarılı Güncelleme: {lastUpdated}</span>
            </div>
          )}
          {processedData && (
            <div className="supplier-payment-container__processed-data">
              <p>İşlem Detayları:</p>
              <ul>
                <li>Yeni Kayıtlar: {processedData.new_records || 0}</li>
                <li>Buffer Kayıtlar: {processedData.buffer_records || 0}</li>
                <li>Atlanan Kayıtlar: {processedData.skipped_records || 0}</li>
              </ul>
            </div>
          )}
        </div>
      )}

      {!loading && !error && localDbSupplierPayments.length === 0 && (
        <p className="supplier-payment-container__no-data">
          Henüz veri yüklenmedi. Lütfen veri çekmek için yukarıdaki butonları kullanın.
        </p>
      )}

      {localDbSupplierPayments.length > 0 && <SupplierPaymentTable />}
      
      <SupplierPaymentUpdates messages={messages} />
    </div>
  );
};

export default TunaInsSupplierPaymentContainer;