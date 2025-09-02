// frontend/src/components/CustomerSales/utils/DynamicSubTotal.js
import React from 'react';
import FormatNumber from './FormatNumber';

const DynamicSubTotal = ({ data, columnId }) => {
  // Her bir satır için belirtilen sütun id'sine göre değerleri toplar
  const total = React.useMemo(() => {
    return data.reduce((sum, current) => {
      const value = Number(current.values[columnId]) || 0;
      return sum + value;
    }, 0);
  }, [data, columnId]);

  // FormatNumber bileşeni ile formatlanmış sayıyı döndürün
  return <FormatNumber value={total} />;
};

export default DynamicSubTotal;
