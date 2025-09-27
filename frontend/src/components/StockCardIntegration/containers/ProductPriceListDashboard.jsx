// path: frontend/src/components/StockCardIntegration/containers/ProductPriceListDashboard.jsx

import React from 'react';
import ProductPriceListTable from './ProductPriceListTable';
import ProductPriceListRefreshButton from './ProductPriceListRefreshButton';
import useProductPriceList from '../hooks/useProductPriceList';
import styles from '../css/ProductPriceListTable.module.css';

const ProductPriceListDashboard = () => {
  const { productPriceList, isLoading, error, refresh } = useProductPriceList();

  return (
    <div className={styles['product-price-list']}>
      {/* 🔷 Başlık + Yenile Butonu aynı satırda */}
      <div className={styles['product-price-list__header-row']}>
        <h3 className={styles['product-price-list__title']}>Ürün Fiyat Listesi</h3>
        <ProductPriceListRefreshButton onSuccess={refresh} />
      </div>

      {/* ⏳ Yükleniyor veya ❌ Hata */}
      {isLoading && <p>⏳ Veriler yükleniyor...</p>}
      {error && <p style={{ color: 'red' }}>Hata: {error.message}</p>}

      {/* ✅ Tablo gösterimi */}
      {!isLoading && !error && productPriceList.length > 0 && (
        <ProductPriceListTable data={productPriceList} />
      )}
    </div>
  );
};

export default ProductPriceListDashboard;



