// path: frontend/src/components/StockCardIntegration/containers/ProductPriceListRefreshButton.jsx

import React from 'react';
import { useMutation } from '@tanstack/react-query';
import { toast } from 'react-toastify';
import { refreshProductPriceList } from '../api/productPriceListApi';
import styles from '../css/ProductPriceListTable.module.css';

const ProductPriceListRefreshButton = ({ onSuccess }) => {
  const { mutate } = useMutation({
    mutationFn: refreshProductPriceList,
    onMutate: () => {
      toast.info('📡 Fiyat listesi güncelleniyor, lütfen bekleyiniz...', {
        toastId: 'price-refreshing',
      });
    },
    onSuccess: (res) => {
      toast.dismiss('price-refreshing');
      toast.success(`✅ Fiyat listesi güncellendi (${res.updated} kayıt)`);
      onSuccess?.();
    },
    onError: (err) => {
      toast.dismiss('price-refreshing');
      toast.error(`❌ Güncelleme başarısız: ${err?.response?.data?.detail || err.message}`);
    },
  });

  return (
    <button
      className={styles['product-price-list__refresh-btn']} // ✅ Doğru className
      onClick={() => mutate()}
    >
      🔄 Fiyat Listesini Yenile
    </button>
  );
};

export default ProductPriceListRefreshButton;
