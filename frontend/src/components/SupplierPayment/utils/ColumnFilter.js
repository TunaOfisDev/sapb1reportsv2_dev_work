// frontend/src/components/SupplierPayment/utils/ColumnFilter.js
import React from 'react';

const ColumnFilter = ({ column }) => {
  const { filterValue, setFilter } = column;
  
  const handleFocus = () => {
    column.toggleSortBy(false, true); // Sıralamayı kaldır
    column.disableSortBy = true; // Sıralamayı devre dışı bırak
  };

  const handleBlur = () => {
    column.disableSortBy = false; // Sıralamayı tekrar etkinleştir
  };

  const handleFilterChange = (e) => {
    setFilter(e.target.value || undefined);
  };

  return (
    <span className="filter-container">
      <input
        value={filterValue || ''}
        onChange={handleFilterChange}
        onFocus={handleFocus}
        onBlur={handleBlur}
        placeholder="Ara..."
      />
    </span>
  );
};

export default ColumnFilter;
