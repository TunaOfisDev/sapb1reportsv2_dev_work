// frontend/src/components/CustomerCollection/containers/CustomerCollectionContainer.js
import React from 'react';
import useCustomerCollection from '../hooks/useCustomerCollection';
import CustomerCollectionTable from './CustomerCollectionTable';
import '../css/CustomerCollectionContainer.css';

const CustomerCollectionContainer = () => {
  const {
    localDbCustomerCollections,
    lastUpdated,
    loading,
    error,
    fetchLocalDbCustomerCollections,
    fetchHanaDbCustomerCollection,
    fetchLastUpdatedCustomerCollection,
    exportCustomerCollectionsToXLSX,
  } = useCustomerCollection();

  /* ----------------------------------------------------------
   * HANA → tablo → zaman damgası sırasıyla yenilenir
   * ---------------------------------------------------------- */
  const handleFetchDataAndUpdateTime = async () => {
    await fetchHanaDbCustomerCollection();        // 1 HANA’dan anlık veri çek
    await fetchLocalDbCustomerCollections();      // 2 lokal tabloyu yeniden doldur
    await fetchLastUpdatedCustomerCollection();   // 3 güncelleme zamanını yenile
  };

  return (
    <div className="customer-collection-container">
      <div className="customer-collection-container__header">
        <h1 className="customer-collection-container__title">Müşteri Tahsilat Listesi</h1>

        <p className="customer-collection-container__last-updated">
          {lastUpdated ? `Son Güncellenme: ${lastUpdated}` : ''}
        </p>

        <div className="customer-collection-container__actions">
          <button
            onClick={fetchLocalDbCustomerCollections}
            className="customer-collection-container__button"
          >
            Yerel Veri Çek
          </button>

          <button
            onClick={handleFetchDataAndUpdateTime}
            className="customer-collection-container__button"
          >
            HANA Anlık Veri Çek
          </button>

          <button
            onClick={exportCustomerCollectionsToXLSX}
            className="customer-collection-container__button"
          >
            Excel'e Aktar
          </button>
        </div>
      </div>

      {loading && <p>Yükleniyor…</p>}
      {error && <p className="error-message">Müşteri koleksiyon verileri yüklenirken hata oluştu.</p>}
      {!loading && !error && localDbCustomerCollections.length === 0 && (
        <p>Veri bulunamadı. Lütfen veri çekmek için yukarıdaki butonları kullanın.</p>
      )}

      {localDbCustomerCollections.length > 0 && (
        <CustomerCollectionTable data={localDbCustomerCollections} />
      )}
    </div>
  );
};

export default CustomerCollectionContainer;

