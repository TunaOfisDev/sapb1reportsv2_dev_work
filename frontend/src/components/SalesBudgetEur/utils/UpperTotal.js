// frontend/src/components/SalesBudgetEur/utils/UpperTotal.js

import { useState, useEffect, useCallback } from 'react';

// Kullanılacak flat key'ler (transformRow ile eşleşmeli)
const keys = [
  'toplam_gercek', 'toplam_hedef',
  'oca_gercek', 'oca_hedef', 'sub_gercek', 'sub_hedef', 'mar_gercek', 'mar_hedef',
  'nis_gercek', 'nis_hedef', 'may_gercek', 'may_hedef', 'haz_gercek', 'haz_hedef',
  'tem_gercek', 'tem_hedef', 'agu_gercek', 'agu_hedef', 'eyl_gercek', 'eyl_hedef',
  'eki_gercek', 'eki_hedef', 'kas_gercek', 'kas_hedef', 'ara_gercek', 'ara_hedef'
];

/**
 * useUpperTotal
 * – SalesBudgetEUR tablosu icin tum kolonlarin toplamlarini hesaplar
 * – transformRow() fonksiyonu ile flatten edilmis verilerle uyumludur
 */
const useUpperTotal = (data = []) => {
  const calculateTotals = useCallback((rows) => {
    const initialTotals = keys.reduce((acc, key) => ({ ...acc, [key]: 0 }), {});

    if (!Array.isArray(rows)) return initialTotals;

    return rows.reduce((acc, row) => {
      keys.forEach((key) => {
        const val = parseFloat(row?.[key] ?? 0);
        acc[key] += !isNaN(val) ? val : 0;
      });
      return acc;
    }, initialTotals);
  }, []);

  const [totals, setTotals] = useState(() => calculateTotals(data));

  useEffect(() => {
    setTotals(calculateTotals(data));
  }, [data, calculateTotals]);

  return totals;
};

export default useUpperTotal;
