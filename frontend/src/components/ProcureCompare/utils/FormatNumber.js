// File: frontend/src/components/ProcureCompare/utils/FormatNumber.js

/**
 * Sayıyı Türkçe formatta gösterir.
 * @param {number|string} value - Sayısal değer
 * @param {number} [decimalDigits=2] - Opsiyonel: ondalık basamak sayısı
 * @returns {string}
 */
const formatNumber = (value, decimalDigits = 2) => {
  if (value === null || value === undefined) return '-';

  const numericValue =
    typeof value === 'string'
      ? parseFloat(value.replace(',', '.').replace(/[^\d.-]/g, ''))
      : Number(value);

  if (isNaN(numericValue)) return '-';

  return numericValue.toLocaleString('tr-TR', {
    minimumFractionDigits: decimalDigits,
    maximumFractionDigits: decimalDigits,
  });
};

export default formatNumber;
