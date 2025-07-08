// frontend/src/components/SalesOfferDocSum/utils/ColumnFilter.js
import React from 'react';
import '../css/ColumnFilter.css';

const ColumnFilter = ({ column }) => {
  const { filterValue, setFilter } = column;

  const handleInputChange = (e) => {
    setFilter(e.target.value);
  };

  const stopPropagation = (e) => {
    e.stopPropagation();
  };

  return (
    <span className="sales-offer-doc-sum__filter" onClick={stopPropagation}>
      <input
        value={filterValue || ''}
        onChange={handleInputChange}
        placeholder="Ara..."
        className="sales-offer-doc-sum__filter-input"
      />
    </span>
  );
};

export default ColumnFilter;