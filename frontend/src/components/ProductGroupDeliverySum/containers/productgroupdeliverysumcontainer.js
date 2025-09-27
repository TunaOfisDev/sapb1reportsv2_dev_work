// frontend/src/components/ProductGroupDeliverySum/containers/productgroupdeliverysumcontainer.js
import React, { useState } from 'react';
import useProductGroupDeliverySum from '../hooks/useProductGroupDeliverySum';
import ProductGroupDeliverySumTable from './productgroupdeliverysumtable';
import '../css/productgroupdeliverysumcontainer.css';

const ProductGroupDeliverySumContainer = () => {
  const {
    currentYearData,
    previousYearData,
    loading,
    error,
    handleFetchLocalData,
    handleFetchHanaData,
    handleYearChange
  } = useProductGroupDeliverySum();

  const [infoMessage, setInfoMessage] = useState('');

  const currentYear = new Date().getFullYear();
  const previousYear = currentYear - 1;

  // 💡 HANA verisi + karşılaştırmalı veri birlikte çekilsin
  const handleRefreshFromHana = async () => {
    setInfoMessage('');
    await handleFetchHanaData();       // HANA'dan canlı veri
    await handleYearChange(currentYear); // Yıl karşılaştırma verilerini tetikle
    setInfoMessage('✅');
  };

  if (loading) return <div className="product-group-delivery-container__loading">Yükleniyor...</div>;
  if (error) return <div className="product-group-delivery-container__error">Hata: {error}</div>;

  return (
    <div className="product-group-delivery-container">
      <div className="product-group-delivery-container__header">
        <h2 className="product-group-delivery-container__title">Sevk İrsaliye Tutar Aylık</h2>
        <div className="product-group-delivery-container__actions">
          <button onClick={handleFetchLocalData} className="product-group-delivery-container__button">
            Yerel Veri Çek
          </button>
          <button onClick={handleRefreshFromHana} className="product-group-delivery-container__button">
            HANA'dan Canlı Veri Çek
          </button>
        </div>
        {infoMessage && (
          <div className="product-group-delivery-container__info">{infoMessage}</div>
        )}
      </div>

      <div className="product-group-delivery-container__tables">
        {/* Güncel Yıl Tablosu */}
        <div className="product-group-delivery-container__table-section">
          <h2 className="product-group-delivery-container__subtitle">{currentYear} Verileri</h2>
          <ProductGroupDeliverySumTable 
            data={currentYearData} 
            year={currentYear}
          />
        </div>

        {/* Önceki Yıl Tablosu */}
        <div className="product-group-delivery-container__table-section">
          <h2 className="product-group-delivery-container__subtitle">{previousYear} Verileri</h2>
          <ProductGroupDeliverySumTable 
            data={previousYearData} 
            year={previousYear}
          />
        </div>
      </div>
    </div>
  );
};

export default ProductGroupDeliverySumContainer;
