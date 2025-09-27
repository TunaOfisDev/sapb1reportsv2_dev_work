// path: frontend/src/components/StockCardIntegration/views/ProductPriceListView.jsx

import React, { useEffect } from 'react';
import useProductPriceList from '../hooks/useProductPriceList';
import styles from '../css/ProductPriceListTable.module.css';

const ProductPriceListView = () => {
  const {
    priceList,
    loading,
    error,
    refreshLivePriceList,
  } = useProductPriceList();

  // Sayfa yüklendiğinde canlı veriyi çek
  useEffect(() => {
    refreshLivePriceList();
  }, [refreshLivePriceList]);

  return (
    <div className={styles['product-price-list']}>
      <h2 className={styles['product-price-list__title']}>Ürün Fiyat Listesi (Canlı)</h2>

      {loading && <p>🔄 Yükleniyor...</p>}
      {error && <p style={{ color: 'red' }}>⚠️ Hata: {error}</p>}

      {!loading && !error && (
        <table className={styles['product-price-list__table']}>
          <thead>
            <tr>
              <th>Ürün Kodu</th>
              <th>Ürün Adı</th>
              <th>Fiyat Listesi</th>
              <th>Fiyat</th>
              <th>Döviz</th>
              <th>Eski Kod</th>
              <th>Güncelleme</th>
            </tr>
          </thead>
          <tbody>
            {priceList.map((item) => (
              <tr key={item.id}>
                <td>{item.item_code}</td>
                <td>{item.item_name}</td>
                <td>{item.price_list_name}</td>
                <td>
                  <span className={styles['product-price-list__price--currency']}>
                    {parseFloat(item.price).toFixed(2)}
                  </span>
                </td>
                <td>{item.currency}</td>
                <td className={styles['product-price-list__old-component']}>
                  {item.old_component_code || '-'}
                </td>
                <td>{new Date(item.updated_at).toLocaleString('tr-TR')}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
};

export default ProductPriceListView;
