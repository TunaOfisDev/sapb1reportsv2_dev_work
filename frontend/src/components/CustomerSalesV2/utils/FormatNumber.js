// frontend/src/components/CustomerSalesV2/utils/FormatNumber.js
import PropTypes from 'prop-types';

/**
 * Sayısal bir değeri, Türkiye'ye uygun para formatında (binlik ayraç, 2 ondalık) string'e çevirir.
 * Değer null, undefined veya sayı değilse '0,00' döndürür.
 */
const FormatNumber = ({ value }) => {
  const num = parseFloat(value);
  if (isNaN(num)) {
    return '0,00';
  }
  return num.toLocaleString('tr-TR', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  });
};

FormatNumber.propTypes = {
  value: PropTypes.oneOfType([PropTypes.string, PropTypes.number]),
};

export default FormatNumber; // `formatNumber` değil, bileşen olarak export edelim
export const formatNumber = (value) => { // Hook içinde kullanmak için fonksiyon hali
    const num = parseFloat(value);
    if (isNaN(num)) return '0,00';
    return num.toLocaleString('tr-TR', {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2,
    });
};