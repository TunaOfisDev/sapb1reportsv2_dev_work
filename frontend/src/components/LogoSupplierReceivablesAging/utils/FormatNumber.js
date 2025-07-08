// frontend/src/components/LogoSupplierReceivablesAging/utils/FormatNumber.js


const FormatNumber = ({ value }) => {
    const number = parseFloat(value); // Sayıyı ondalık olarak ayrıştır
    const formattedNumber = number.toLocaleString('tr-TR', {
        minimumFractionDigits: 0,
        maximumFractionDigits: 0
    }); // Küsuratları kaldırarak formatla

    return <div className="supplier-payment__td--numeric">{formattedNumber}</div>;
};

export default FormatNumber;
