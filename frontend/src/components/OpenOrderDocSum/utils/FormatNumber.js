// frontend/src/components/OpenOrderDocSum/utils/FormatNumber.js
import '../css/OpenOrderDocSumTable.css';

const FormatNumber = ({ value, className }) => {
  const number = isNaN(parseFloat(value)) ? 0 : parseFloat(value); // NaN değerleri 0 ile değiştir
  const formattedNumber = number.toLocaleString('tr-TR', {
    maximumFractionDigits: 0
  });
  return <div className={className}>{formattedNumber}</div>;
};


export default FormatNumber;

