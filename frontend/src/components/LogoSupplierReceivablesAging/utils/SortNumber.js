// frontend/src/components/LogoSupplierReceivablesAging/utils/SortNumber.js
const numberSort = (rowA, rowB, columnId, desc) => {
  const a = rowA.values[columnId] !== null && rowA.values[columnId] !== undefined 
    ? parseFloat(rowA.values[columnId]) 
    : 0;

  const b = rowB.values[columnId] !== null && rowB.values[columnId] !== undefined 
    ? parseFloat(rowB.values[columnId]) 
    : 0;

  if (a > b) return 1;
  if (a < b) return -1;
  return 0;
};

// Mutlak değer sıralaması (isteğe bağlı kullanım için korunuyor)
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

export { numberSort, absSort };