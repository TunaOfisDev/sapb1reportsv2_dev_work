// frontend/src/components/TunaInsTotalRisk/utils/UpperTotal.js
import { useState, useEffect, useRef, useCallback } from 'react';

// Vanilla JavaScript ile derin karşılaştırma fonksiyonu
const deepEqual = (a, b) => {
  if (a === b) return true;
  if (typeof a !== 'object' || typeof b !== 'object' || a === null || b === null) return false;

  const keysA = Object.keys(a);
  const keysB = Object.keys(b);

  if (keysA.length !== keysB.length) return false;

  for (let key of keysA) {
    if (!keysB.includes(key) || !deepEqual(a[key], b[key])) return false;
  }

  return true;
};

const keys = ['tahsilat', 'bakiye', 'acik_teslimat', 'acik_siparis', 'avans_bakiye', 'toplam_risk'];

const useUpperTotal = (data = []) => {
  // calculateTotals fonksiyonunu useCallback ile sarmalayarak referansın sabit kalmasını sağlıyoruz
  const calculateTotals = useCallback((data) => {
    if (!data || !Array.isArray(data)) {
      return keys.reduce((acc, key) => ({ ...acc, [key]: 0 }), {});
    }

    return data.reduce((acc, row) => {
      keys.forEach(key => {
        const value = parseFloat(row[key]);
        acc[key] = (acc[key] || 0) + (isNaN(value) ? 0 : value);
      });
      return acc;
    }, keys.reduce((acc, key) => ({ ...acc, [key]: 0 }), {}));
  }, []);

  const [uptotals, setUptotals] = useState(calculateTotals(data));
  const prevDataRef = useRef(); // Önceki veriyi saklamak için useRef kullanıyoruz

  // Derin karşılaştırma ile data değiştiğinde toplamları hesapla
  useEffect(() => {
    if (!deepEqual(prevDataRef.current, data)) {
      setUptotals(calculateTotals(data));
      prevDataRef.current = data; // Mevcut veriyi sakla
    }
  }, [data, calculateTotals]);

  return uptotals;
};

export default useUpperTotal;

