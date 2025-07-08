// frontend/src/components/SalesBudgetEur/utils/FormatNumber.js


const FormatNumber = ({ value, className }) => {
  // Sayıyı tam sayıya çevir
  const number = parseInt(value, 10);
  // Locale string'e çevirerek istenilen formatı elde et
  const formattedNumber = number.toLocaleString('tr-TR');

  return <div className={className}>{formattedNumber}</div>; // Burada bir div ile sarmaladık ve className prop'unu ekledik
};

export default FormatNumber;

  