// frontend/src/components/LogoSupplierReceivablesAging/utils/UpperTotal.js
import { useState, useEffect } from 'react';

const useUpperTotal = (data) => {
  const calculateTotals = (data) => {
    const initialTotals = { guncel_bakiye: 0, aylik_kalan_alacak: {} };

    if (data.length > 0) {
      // Tüm satırlardan ay anahtarlarının birleşimini al
      const allMonths = new Set();
      data.forEach((row) => {
        Object.keys(row.aylik_kalan_alacak || {}).forEach((month) => {
          allMonths.add(month);
        });
      });

      // Aylık bakiyeler için initialTotals doldur
      allMonths.forEach((month) => {
        initialTotals.aylik_kalan_alacak[month] = 0;
      });
    }

    return data.reduce((acc, row) => {
      // Güncel bakiyeyi topla
      const currentBalanceValue = parseFloat(row.guncel_bakiye);
      acc.guncel_bakiye += isNaN(currentBalanceValue) ? 0 : currentBalanceValue;

      // Aylık bakiyeleri topla
      Object.entries(row.aylik_kalan_alacak || {}).forEach(([month, balance]) => {
        const balanceValue = parseFloat(balance);
        acc.aylik_kalan_alacak[month] += isNaN(balanceValue) ? 0 : balanceValue;
      });

      return acc;
    }, initialTotals);
  };

  const [uptotals, setUptotals] = useState(calculateTotals(data));

  useEffect(() => {
    setUptotals(calculateTotals(data));
  }, [data]);

  return uptotals;
};

export default useUpperTotal;