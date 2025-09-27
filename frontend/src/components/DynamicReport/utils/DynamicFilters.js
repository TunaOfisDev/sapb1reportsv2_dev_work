// frontend/src/components/DynamicReport/utils/DynamicFilters.js
import React from 'react';
import { useAsyncDebounce } from 'react-table';

const DynamicFilters = ({ columns, setFilter }) => {
  const debouncedSetFilter = useAsyncDebounce((id, value) => {
    setFilter(id, value.toUpperCase()); // Girişi büyük harfe dönüştürün
  }, 500); // 500 ms debounce süresi

  return (
    <tr className="dynamic-filters">
      {columns.map((column, index) => (
        <th className="dynamic-filters__cell" key={index}>
          <input
            className="dynamic-filters__input"
            type="text"
            placeholder={`Filter ${column.Header}`}
            onChange={(e) => {
              debouncedSetFilter(column.id, e.target.value);
            }}
          />
        </th>
      ))}
    </tr>
  );
};

export default DynamicFilters;