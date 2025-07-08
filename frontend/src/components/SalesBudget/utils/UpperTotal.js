// frontend/src/components/SalesBudget/utils/UpperTotal.js
import { useState, useEffect, useCallback } from 'react';

const keys = [
  'toplam_gercek', 'toplam_hedef', 'oca_gercek', 'oca_hedef', 'sub_gercek', 'sub_hedef',
  'mar_gercek', 'mar_hedef', 'nis_gercek', 'nis_hedef', 'may_gercek', 'may_hedef',
  'haz_gercek', 'haz_hedef', 'tem_gercek', 'tem_hedef', 'agu_gercek', 'agu_hedef',
  'eyl_gercek', 'eyl_hedef', 'eki_gercek', 'eki_hedef', 'kas_gercek', 'kas_hedef',
  'ara_gercek', 'ara_hedef'
];

const useUpperTotal = (data = []) => {
  // Veriyi hesaplayan fonksiyonu useCallback ile optimize ediyoruz
  const calculateTotals = useCallback((data) => {
    // Eğer data boş veya yanlış bir formatta ise başlangıç değerlerini sıfır olarak döndür
    if (!data || !Array.isArray(data)) {
      return keys.reduce((acc, key) => ({ ...acc, [key]: 0 }), {});
    }

    return data.reduce((acc, row) => {
      keys.forEach(key => {
        const value = parseFloat(row[key]); // Veriyi sayıya çeviriyoruz
        acc[key] = (acc[key] || 0) + (!isNaN(value) ? value : 0); // NaN olan değerleri sıfır kabul ediyoruz
      });
      return acc;
    }, keys.reduce((acc, key) => ({ ...acc, [key]: 0 }), {})); // Başlangıçta tüm toplamları sıfır olarak ayarlıyoruz
  }, []);

  const [uptotals, setUptotals] = useState(calculateTotals(data));

  // Data değiştiğinde toplamları yeniden hesapla
  useEffect(() => {
    setUptotals(calculateTotals(data));
  }, [data, calculateTotals]);

  return uptotals;
};

export default useUpperTotal;
