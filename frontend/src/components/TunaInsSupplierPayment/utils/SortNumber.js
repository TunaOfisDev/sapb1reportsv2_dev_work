// frontend/src/components/TunaInsSupplierPayment/utils/SortNumber.js
const absSort = (rowA, rowB, columnId, desc) => {
  const a = rowA.values[columnId] !== null && rowA.values[columnId] !== undefined 
    ? Math.abs(parseFloat(rowA.values[columnId])) 
    : 0;

  const b = rowB.values[columnId] !== null && rowB.values[columnId] !== undefined 
    ? Math.abs(parseFloat(rowB.values[columnId])) 
    : 0;

  if (a > b) return 1;
  if (a < b) return -1;
  return 0;
};

export default absSort;

