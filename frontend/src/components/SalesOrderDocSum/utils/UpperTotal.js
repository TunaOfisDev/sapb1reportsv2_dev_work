// frontend/src/components/SalesOrderDocSum/utils/UpperTotal.js
import { useState, useEffect, useRef, useCallback } from 'react';
import isEqual from 'lodash.isequal';

// keys sabit olduğu için fonksiyonun dışında tanımlayalım
const keys = ['net_tutar_ypb', 'net_tutar_spb', 'acik_net_tutar_ypb', 'acik_net_tutar_spb'];

const useUpperTotal = (data = []) => {
  
  // calculateTotals fonksiyonunu useCallback ile sarmalayarak referansın sabit kalmasını sağlıyoruz
  const calculateTotals = useCallback((data) => {
    // Boş veri kontrolü
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
  }, []); // keys dışarıda tanımlandığı için buraya bağımlılık olarak eklemeye gerek yok

  const [uptotals, setUptotals] = useState(calculateTotals(data));
  const prevDataRef = useRef(); // Önceki veriyi saklamak için useRef kullanıyoruz

  // Derin karşılaştırma ile data değiştiğinde toplamları hesapla
  useEffect(() => {
    if (!isEqual(prevDataRef.current, data)) {
      setUptotals(calculateTotals(data));
      prevDataRef.current = data; // Mevcut veriyi sakla
    }
  }, [data, calculateTotals]); // Sadece data değiştiğinde tetikle

  return uptotals;
};

export default useUpperTotal;



