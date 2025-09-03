// frontend/src/components/CustomerSalesV2/utils/FormatNumber.js
import PropTypes from 'prop-types';

/**
 * GÜNCELLEME: Sayısal bir değeri, Türkiye'ye uygun para formatında 
 * (binlik ayraç, ONDALIK KISIM OLMADAN) string'e çevirir.
 * Değer null, undefined veya sayı değilse '0' döndürür.
 */
const FormatNumber = ({ value }) => {
  const num = parseFloat(value);
  if (isNaN(num)) {
    // GÜNCELLEME: Ondalık olmadığı için '0,00' yerine '0' döndürüyoruz.
    return '0';
  }
  // GÜNCELLEME: Ondalık basamakları kaldırıyoruz.
  return num.toLocaleString('tr-TR', {
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  });
};

FormatNumber.propTypes = {
  value: PropTypes.oneOfType([PropTypes.string, PropTypes.number]),
};

export default FormatNumber;

export const formatNumber = (value) => {
    const num = parseFloat(value);
    // GÜNCELLEME: Ondalık olmadığı için '0,00' yerine '0' döndürüyoruz.
    if (isNaN(num)) return '0';
    // GÜNCELLEME: Ondalık basamakları kaldırıyoruz.
    return num.toLocaleString('tr-TR', {
        minimumFractionDigits: 0,
        maximumFractionDigits: 0,
    });
};