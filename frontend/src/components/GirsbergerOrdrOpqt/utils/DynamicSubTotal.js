// frontend/src/components/OpenOrderDocSum/utils/DynamicSubTotal.js
import { useMemo } from 'react';

const useDynamicSubtotals = (rows, idAccessor, valueAccessors) => {
  const subtotals = useMemo(() => {
    const initSubtotals = valueAccessors.reduce((acc, valueAccessor) => {
      acc[valueAccessor] = 0;
      return acc;
    }, {});

    // `rows` artık filtreden geçirilmiş ve ekranda gösterilen satırları içeriyor.
    rows.forEach(row => {
      valueAccessors.forEach(valueAccessor => {
        const rawValue = row.values[valueAccessor];
        const value = rawValue !== undefined ? parseFloat(rawValue) : 0;
        if (!isNaN(value)) {
          initSubtotals[valueAccessor] += value;
        }
      });
    });

    return initSubtotals;
  }, [rows, valueAccessors]);

  return subtotals;
};

export default useDynamicSubtotals;

