// frontend/src/components/TunaInsTotalRisk/utils/FormatNumber.js
import '../css/TotalRiskTable.css';

  
const FormatNumber = ({ value, className }) => {
  // Sayıyı ondalıklı sayıya çevir ve negatif değerleri koru
  const number = parseFloat(value);
  // Locale string'e çevirerek istenilen formatı elde et ve ondalık kısmı gösterme
  const formattedNumber = number.toLocaleString('tr-TR', {
    maximumFractionDigits: 0 // Ondalık kısmı göstermemek için
  });

  return <div className={className}>{formattedNumber}</div>;
};

export default FormatNumber;
