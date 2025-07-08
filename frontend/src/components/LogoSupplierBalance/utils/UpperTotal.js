// frontend/src/components/OpenOrderDocSum/utils/UpperTotal.js
import { useState, useEffect, useCallback } from 'react';

// Toplamların hesaplanacağı anahtarları tanımla
const keys = ['net_tutar_ypb', 'net_tutar_spb', 'acik_net_tutar_ypb', 'acik_net_tutar_spb'];

const useUpperTotal = (data = []) => {
  // Veriyi hesaplayan fonksiyon
  const calculateTotals = useCallback((inputData) => {
    // Eğer data boş ya da yanlış formatta ise başlangıç toplamlarını sıfır olarak döndür
    if (!Array.isArray(inputData) || inputData.length === 0) {
      return keys.reduce((acc, key) => ({ ...acc, [key]: 0 }), {});
    }

    return inputData.reduce((acc, row) => {
      if (!row) return acc;

      keys.forEach(key => {
        // Önce her anahtarın var olup olmadığını kontrol et
        if (row.hasOwnProperty(key)) {
          const value = parseFloat(row[key]);
          acc[key] = (acc[key] || 0) + (!isNaN(value) ? value : 0);
        } else {
          // Anahtar mevcut değilse toplamı sıfır olarak koru
          acc[key] = acc[key] || 0;
        }
      });
      return acc;
    }, keys.reduce((acc, key) => ({ ...acc, [key]: 0 }), {})); // Başlangıçta tüm toplamlar 0
  }, []);

  // Başlangıç toplamlarını hesapla
  const [uptotals, setUptotals] = useState(() => calculateTotals(data));

  // Data değiştiğinde toplamları yeniden hesapla
  useEffect(() => {
    setUptotals(calculateTotals(data));
  }, [data, calculateTotals]);

  return uptotals;
};

export default useUpperTotal;

