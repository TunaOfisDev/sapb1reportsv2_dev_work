// frontend/src/components/CustomerSales/utils/RatioToTotalSales.js
import React from 'react';
import { useMemo } from 'react';

const RatioToTotalSales = ({ value, total }) => {
  const ratio = useMemo(() => {
    if (total > 0) {
      return ((value / total) * 100).toFixed(2) + '%'; // Oranı yüzde olarak hesapla ve iki ondalık basamağa yuvarla
    }
    return '0%'; // Total 0 ise, oranı 0% olarak göster
  }, [value, total]);

  return <span>{ratio}</span>;
};

export default RatioToTotalSales;
