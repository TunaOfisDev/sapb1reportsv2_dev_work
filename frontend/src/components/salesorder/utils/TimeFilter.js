// frontend/src/components/salesorder/utils/TimeFilter.js
import React from 'react';

const TimeFilter = ({ onFilterChange }) => {
  // Zaman filtresi seçenekleri
  const filterOptions = [
    { value: 'daily', label: 'Daily' },
    { value: 'weekly', label: 'Weekly' },
    { value: 'monthly', label: 'Monthly' },
    { value: 'quarterly', label: 'Quarterly' },
    { value: 'yearly', label: 'Yearly' },
  ];

  return (
    <div className="time-filter-buttons">
      {filterOptions.map((option) => (
        <button
          key={option.value}
          onClick={() => onFilterChange(option.value)}
          className="time-filter-button"
        >
          {option.label}
        </button>
      ))}
    </div>
  );
};

export default TimeFilter;
