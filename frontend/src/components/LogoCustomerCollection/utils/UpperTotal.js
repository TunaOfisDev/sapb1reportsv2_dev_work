// frontend/src/components/LogoCustomerCollection/utils/UpperTotal.js
import { useState, useEffect } from 'react';

const getMonthEntries = (monthly) => {
  if (!monthly) return [];
  return Array.isArray(monthly)            // [["May25", 123], ...]
    ? monthly
    : Object.entries(monthly);             // {May25: 123, …}
};

const useUpperTotal = (data) => {
  const calc = (rows) => {
    const totals = { guncel_bakiye: 0, aylik_kalan_borc: {} };

    // tüm ay etiketlerini topla
    rows.forEach((r) => {
      getMonthEntries(r.aylik_kalan_borc).forEach(([label]) => {
        if (!(label in totals.aylik_kalan_borc)) totals.aylik_kalan_borc[label] = 0;
      });
    });

    // toplamlara ekle
    rows.forEach((r) => {
      totals.guncel_bakiye += parseFloat(r.guncel_bakiye) || 0;
      getMonthEntries(r.aylik_kalan_borc).forEach(([label, val]) => {
        totals.aylik_kalan_borc[label] += parseFloat(val) || 0;
      });
    });

    return totals;
  };

  const [uptotals, setUptotals] = useState(calc(data));
  useEffect(() => setUptotals(calc(data)), [data]);
  return uptotals;
};

export default useUpperTotal;


