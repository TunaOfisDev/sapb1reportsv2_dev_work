// frontend/src/components/SalesInvoiceSum/utils/SortNumber.js

const SortNumber = (useAbsolute = false) => (rowA, rowB, columnId) => {
  const getValue = (val) => {
    const number = parseFloat(val) || 0;
    return useAbsolute ? Math.abs(number) : number;
  };

  const valA = getValue(rowA.values[columnId]);
  const valB = getValue(rowB.values[columnId]);
  
  return valA - valB;
};

export default SortNumber;