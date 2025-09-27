// frontend/src/components/SalesOrderDocSum/utils/FormatNumber.js
const FormatNumber = ({ value, className }) => {
  // Sayıyı ondalıklı sayıya çevir ve negatif değerleri koru
  const number = parseFloat(value);
  // NaN ise 0 olarak ayarla
  const safeNumber = isNaN(number) ? 0 : number;
  // Türkçe locale ile sayıyı formatla ve 2 ondalık basamak göster
  const formattedNumber = safeNumber.toLocaleString('tr-TR', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
    useGrouping: true
  });

  return <div className={className}>{formattedNumber}</div>;
};

export default FormatNumber;

