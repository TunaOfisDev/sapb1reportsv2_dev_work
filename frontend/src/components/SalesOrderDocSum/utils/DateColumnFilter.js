// frontend/src/components/OpenOrderDocSum/utils/DateColumnFilter.js
import React, { useState } from 'react';
import '../css/SalesOrderDocSumTable.css';

const formatDateForBackend = (dateString) => {
  const parts = dateString.split('.');
  return `${parts[2]}-${parts[1]}-${parts[0]}`;
};

const DateColumnFilter = ({ column }) => {
  const { filterValue, setFilter } = column;
  const [inputValue, setInputValue] = useState('');

  const handleInputChange = (e) => {
    const value = e.target.value;
    setInputValue(value);
    if (value.length === 10) {
      const formattedDate = formatDateForBackend(value);
      setFilter(formattedDate);
    } else {
      setFilter(undefined);
    }
  };

  const handleClick = (e) => {
    e.stopPropagation();
  };

  return (
    <div className="sales-order-doc-sum-table__filter--date sales-order-doc-sum-table__filter--sap-yellow">
      <input
        value={inputValue}
        onChange={handleInputChange}
        onClick={handleClick}
        placeholder='GG.AA.YYYY'
      />
    </div>
  );
};

export default DateColumnFilter;