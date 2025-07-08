
// frontend/src/components/Activities/utils/ColumnFilter.js
import React from 'react';

/** Ortak sütun filtresi – sort tetiklemez */
const ColumnFilter = ({
  column: { filterValue, setFilter, preFilteredRows },
}) => {
  const totalRows = preFilteredRows?.length ?? 0;

  return (
    <input
      value={filterValue || ''}
      onChange={e => setFilter(e.target.value || undefined)}
      onClick={e => e.stopPropagation()}
      onFocus={e => e.stopPropagation()}
      placeholder={`Ara (${totalRows})...`}
      className="columnfilter__input"
      autoComplete="off"
    />
  );
};

export default ColumnFilter;
