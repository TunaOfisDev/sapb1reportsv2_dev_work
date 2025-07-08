// frontend/src/components/TotalRisk/utils/ColumnFilter.js
import React from 'react';
import '../css/ColumnFilter.css';

const ColumnFilter = ({ column }) => {
  const { filterValue, setFilter } = column;
  return (
    <span className="totalrisk-columnfilter">
      <input
        value={filterValue || ''}
        onChange={e => setFilter(e.target.value)}
        placeholder={`Ara...`}
        className="totalrisk-columnfilter__input"
      />
    </span>
  );
};

export default ColumnFilter;
