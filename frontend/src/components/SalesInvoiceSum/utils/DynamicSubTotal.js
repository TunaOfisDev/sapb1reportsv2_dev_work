// frontend/src/components/DeliveryDocSumV2/utils/DynamicSubTotal.js
import { useMemo } from 'react';

const useDynamicSubtotals = (rows, valueAccessors) => {
  const subtotals = useMemo(() => {
    const initSubtotals = valueAccessors.reduce((acc, valueAccessor) => {
      acc[valueAccessor] = 0;
      return acc;
    }, {});

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
