// frontend/src/components/TotalRisk/utils/FormatNumber.js
import React from 'react';

const formatNumber = (value) => {
  if (typeof value !== 'number') return value;
  
  // Sayıyı ###.###,## formatına çevir
  let parts = value.toFixed(2).split('.');
  parts[0] = parts[0].replace(/\B(?=(\d{3})+(?!\d))/g, '.');
  return parts.join(',');
};

const FormatNumber = ({ value }) => {
  return <span>{formatNumber(value)}</span>;
};

export default FormatNumber;