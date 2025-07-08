// frontend/src/components/RawMaterialWarehouseStock/utils/ColumnFilter.js
import React from 'react';
import '../css/ColumnFilter.css';

const turkishToUpperCase = (str) => {
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
    <span className="rawmaterial-columnfilter">
      <input
        value={filterValue || ''}
        onChange={handleInputChange}
        placeholder={`Ara...`}
        className="rawmaterial-columnfilter__input"
        onClick={stopPropagation}
      />
    </span>
  );
};

export default ColumnFilter;