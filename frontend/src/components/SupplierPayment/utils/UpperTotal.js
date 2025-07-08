// frontend/src/components/SupplierPayment/utils/UpperTotal.js
import { useState, useEffect } from 'react';

const useUpperTotal = (data) => {
  const calculateTotals = (data) => {
    const initialTotals = { current_balance: 0, monthly_balances: {} };

    if (data.length > 0) {
      // Örnek veriden tüm ayların listesini al
      const allMonths = Object.keys(data[0].monthly_balances);

      // Aylık bakiyeler için initialTotals doldur
      allMonths.forEach(month => {
        initialTotals.monthly_balances[month] = 0;
      });
    }

    return data.reduce((acc, row) => {
      // Güncel bakiyeyi topla
      const currentBalanceValue = parseFloat(row.current_balance);
      acc.current_balance += isNaN(currentBalanceValue) ? 0 : currentBalanceValue;

      // Aylık bakiyeleri topla
      Object.entries(row.monthly_balances).forEach(([month, balance]) => {
        const balanceValue = parseFloat(balance);
        acc.monthly_balances[month] += isNaN(balanceValue) ? 0 : balanceValue;
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

