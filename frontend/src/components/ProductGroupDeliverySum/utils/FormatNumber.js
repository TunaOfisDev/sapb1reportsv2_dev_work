// frontend/src/components/ProductGroupDeliverySum/utils/FormatNumber.js
import React from 'react';  // React import edildi
import '../css/productgroupdeliverysumtable.css';

const FormatNumber = ({ value, className }) => {
  const number = parseFloat(value);
  const formattedNumber = number.toLocaleString('tr-TR', {
    maximumFractionDigits: 0,
  });

  return <div className={className}>{formattedNumber}</div>;
};

export default FormatNumber;