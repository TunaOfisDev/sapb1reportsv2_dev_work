// frontend/src/components/SalesOrderDocSum/utils/ColumnFilter.js
import React from 'react';
import '../css/ColumnFilter.css';

export const turkishToUpperCase = (str) => {
  const turkishChars = {
    'i': 'İ',
    'ı': 'I',
    'ğ': 'Ğ',
    'ü': 'Ü',
    'ş': 'Ş',
    'ö': 'Ö',
    'ç': 'Ç'
  };
  return str.replace(/[iığüşöç]/g, letter => turkishChars[letter]).toUpperCase();
};

const ColumnFilter = ({ column }) => {
  const { filterValue, setFilter } = column;

  const handleInputChange = (e) => {
    const uppercaseValue = turkishToUpperCase(e.target.value);
    setFilter(uppercaseValue);
  };

  const stopPropagation = (e) => {
    e.stopPropagation();
  };

  return (
    <span className="sales-offer-doc-sum__filter" onClick={stopPropagation}>
      <input
        value={filterValue || ''}
        onChange={handleInputChange}
        placeholder={`Ara...`}
        className="sales-offer-doc-sum__filter-input"
      />
    </span>
  );
};

// Default filter for no manipulation
const DefaultFilter = ({ column }) => {
  const { filterValue, setFilter } = column;

  const handleInputChange = (e) => {
    setFilter(e.target.value); // No manipulation, simply sets the value
  };

  const stopPropagation = (e) => {
    e.stopPropagation();
  };

  return (
    <span className="sales-offer-doc-sum__filter" onClick={stopPropagation}>
      <input
        value={filterValue || ''}
        onChange={handleInputChange}
        placeholder={`Ara...`}
        className="sales-offer-doc-sum__filter-input"
      />
    </span>
  );
};

export default ColumnFilter;
export { DefaultFilter }; // Export the new filter