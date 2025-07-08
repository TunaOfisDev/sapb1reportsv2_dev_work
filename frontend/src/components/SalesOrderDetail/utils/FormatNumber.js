// frontend/src/components/SalesOrderDetail/utils/FormatNumber.js
import '../css/SalesOrderDetailTable.css';

const FormatNumber = ({ value }) => {
  const number = parseFloat(value); // parseFloat kullanarak ondalık sayıları da destekleyin
  const formattedNumber = number.toLocaleString('tr-TR'); // Sayıyı yerel string formatına çevirin

  return <div className="sales-order-detail__td--numeric">{formattedNumber}</div>;
};

export default FormatNumber;

  