// frontend/src/components/CustomerCollection/utils/SortNumber.js
export const basicSort = (rowA, rowB, columnId) => {
    let a = rowA.values[columnId] || 0;
    let b = rowB.values[columnId] || 0;
    a = parseFloat(a);
    b = parseFloat(b);
    return a > b ? 1 : a < b ? -1 : 0;
  };
  