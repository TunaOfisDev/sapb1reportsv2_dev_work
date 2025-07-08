// frontend/src/components/SalesInvoiceSum/utils/ColumnFilter.js
import React from 'react';
import '../css/ColumnFilter.css';

const ColumnFilter = ({ column }) => {
  const { filterValue, setFilter } = column;

  const handleClick = (e) => {
    e.stopPropagation();
  };

  return (
    <span className="sales-invoice-sum-columnfilter" onClick={handleClick}>
      <input
        value={filterValue || ''}
        onChange={e => setFilter(e.target.value)}
        onClick={handleClick}
        placeholder={`Ara...`}
        className="sales-invoice-sum-columnfilter__input"
      />
    </span>
  );
};

export default ColumnFilter;