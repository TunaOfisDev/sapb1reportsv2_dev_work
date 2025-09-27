// frontend/src/components/SalesOfferDocSum/utils/UpperTotal.js
import { useState, useEffect, useCallback } from 'react';

const keys = ['brut_tutar_spb', 'net_tutar_spb'];

const useUpperTotal = (data = []) => {
  // calculateTotals fonksiyonunu useCallback ile optimize ediyoruz
  const calculateTotals = useCallback((data) => {
    // Eğer data boş ya da yanlış bir formatta ise, başlangıç değerlerini sıfır olarak döndür
    if (!data || !Array.isArray(data)) {
      return keys.reduce((acc, key) => ({ ...acc, [key]: 0 }), {});
    }

    return data.reduce((acc, row) => {
      keys.forEach(key => {
        const value = parseFloat(row[key]); // Veriyi sayıya çevir
        acc[key] = (acc[key] || 0) + (!isNaN(value) ? value : 0); // NaN olan değerleri sıfır kabul et
      });
      return acc;
    }, keys.reduce((acc, key) => ({ ...acc, [key]: 0 }), {})); // Başlangıçta tüm toplamları sıfır olarak ayarla
  }, []);

  const [uptotals, setUptotals] = useState(calculateTotals(data));

  // Data değiştiğinde tekrar toplam hesaplama
  useEffect(() => {
    setUptotals(calculateTotals(data));
  }, [data, calculateTotals]);

  return uptotals;
};

export default useUpperTotal;

