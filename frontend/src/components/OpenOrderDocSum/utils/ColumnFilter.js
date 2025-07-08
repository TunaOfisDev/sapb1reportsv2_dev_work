// frontend/src/components/OpenOrderDocSum/utils/ColumnFilter.js
import React from 'react';
import '../css/ColumnFilter.css'; 

function DefaultColumnFilter({
  column: { filterValue, preFilteredRows, setFilter, id },
}) {
  const count = preFilteredRows.length;
  
  const handleStopPropagation = (e) => {
    e.stopPropagation();
  };

  return (
    <div className="open-order-doc-sum__filter" onClick={handleStopPropagation}>
      <input
        value={filterValue || ''}
        onChange={e => setFilter(e.target.value)}
        placeholder={`Ara (${count} satır)...`}
      />
    </div>
  );
}

export default DefaultColumnFilter;


