// frontend/src/components/CustomerSales/utils/FormatNumber.js
import '../css/CustomerSalesTable.css';

const FormatNumber = ({ value }) => {
  const number = parseFloat(value); // parseFloat kullanarak ondalık sayıları da destekleyin
  const formattedNumber = number.toLocaleString('tr-TR'); // Sayıyı yerel string formatına çevirin

  return <div className="customer-sales__td--numeric">{formattedNumber}</div>;
};

export default FormatNumber;

  