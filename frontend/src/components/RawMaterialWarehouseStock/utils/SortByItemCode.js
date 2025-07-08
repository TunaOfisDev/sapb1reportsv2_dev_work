// frontend/src/components/RawMaterialWarehouseStock/utils/SortByItemCode.js

const sortByItemCode = (rowA, rowB, columnId) => {
    const codeA = String(rowA.values[columnId]);
    const codeB = String(rowB.values[columnId]);
    return codeA.localeCompare(codeB, undefined, { numeric: true, sensitivity: 'base' });
  };
  
  export default sortByItemCode;
  