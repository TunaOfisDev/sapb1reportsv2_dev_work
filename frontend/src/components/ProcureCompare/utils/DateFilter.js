// File: frontend/src/components/ProcureCompare/utils/DateFilter.js
import React from 'react';
import { formatDateTime } from './DateTimeFormat';
import '../css/ColumnFilter.css';

const DateFilter = ({ column }) => {
  const { filterValue, setFilter } = column;

  return (
    <input
      className="column-filter__input"
      value={filterValue || ''}
      onClick={(e) => e.stopPropagation()}
      onChange={(e) => setFilter(e.target.value)}
      placeholder="Tarih (GG.AA.YYYY)"
    />
  );
};

export const dateIncludesFilterFn = (rows, id, filterValue) => {
  return rows.filter(row => {
    const rawValue = row.values[id];
    const formatted = formatDateTime(rawValue); // DD.MM.YYYY
    return formatted.toLowerCase().includes(filterValue.toLowerCase());
  });
};

export default DateFilter;
