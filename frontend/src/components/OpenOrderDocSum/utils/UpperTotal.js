// frontend/src/components/OpenOrderDocSum/utils/UpperTotal.js
import { useState, useEffect, useCallback } from 'react';

const keys = [
  'acik_net_tutar_ypb',
  'girsberger_net_tutar_ypb',
  'mamul_net_tutar_ypb',
  'ticari_net_tutar_ypb',
  'nakliye_net_tutar_ypb',
  'montaj_net_tutar_ypb'
];

const useUpperTotal = (data = []) => {
  const calculateTotals = useCallback((inputData) => {
    if (!Array.isArray(inputData) || inputData.length === 0) {
      return keys.reduce((acc, key) => ({ ...acc, [key]: 0 }), {});
    }

    return inputData.reduce((acc, row) => {
      if (!row) return acc;
      
      keys.forEach(key => {
        if (key in row) {
          const value = parseFloat(row[key]);
          acc[key] = (acc[key] || 0) + (!isNaN(value) ? value : 0);
        } else {
          acc[key] = acc[key] || 0;
        }
      });
      return acc;
    }, keys.reduce((acc, key) => ({ ...acc, [key]: 0 }), {}));
  }, []);

  const [uptotals, setUptotals] = useState(calculateTotals(data));

  useEffect(() => {
    setUptotals(calculateTotals(data));
  }, [data, calculateTotals]);

  return uptotals;
};

export default useUpperTotal;
