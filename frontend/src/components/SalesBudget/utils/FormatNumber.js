// frontend/src/components/SalesBudget/utils/FormatNumber.js
import '../css/SalesBudgetTable.css';

const FormatNumber = ({ value, className }) => {
  // Sayıyı tam sayıya çevir
  const number = parseInt(value, 10);
  // Locale string'e çevirerek istenilen formatı elde et
  const formattedNumber = number.toLocaleString('tr-TR');

  return <div className={className}>{formattedNumber}</div>; // Burada bir div ile sarmaladık ve className prop'unu ekledik
};

export default FormatNumber;

  