// frontend/src/components/OpenOrderDocSum/utils/UpperTotal.js
import { useState, useEffect } from 'react';

const useUpperTotal = (data) => {
  const keys = ['net_tutar_ypb',  'net_tutar_spb', 'acik_net_tutar_ypb', 'acik_net_tutar_spb'];

  const calculateTotals = (data) => {
    return data.reduce((acc, row) => {
      keys.forEach(key => {
        const value = parseFloat(row[key]);
        acc[key] = (acc[key] || 0) + (isNaN(value) ? 0 : value);
      });
      return acc;
    }, keys.reduce((acc, key) => ({ ...acc, [key]: 0 }), {}));
  };

  const [uptotals, setUptotals] = useState(calculateTotals(data));

  useEffect(() => {
    setUptotals(calculateTotals(data));
  }, [data]);

  return uptotals;
};

export default useUpperTotal;
