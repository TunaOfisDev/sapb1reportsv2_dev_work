// File: frontend/src/components/ProcureCompare/utils/ColumnFilter.js
import React from 'react';
import '../css/ColumnFilter.css';

const ColumnFilter = ({ column }) => {
  const { filterValue, setFilter } = column;

  return (
    <input
      className="column-filter__input"
      value={filterValue || ''}
      onClick={(e) => e.stopPropagation()} 
      onChange={e => setFilter(e.target.value)}
      placeholder="Filtrele..."
    />
  );
};

export default ColumnFilter;
