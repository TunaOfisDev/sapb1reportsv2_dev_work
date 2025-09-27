// frontend/src/components/TunaInsSupplierAdvanceBalance/utils/DynamicButtonFilters.js
import React, { useState } from 'react';
import PropTypes from 'prop-types';
import '../css/DynamicButtonFilters.css';

const buttonFilters = [
  { prefix: '320.14', label: 'Hadımköy' },
  { prefix: '320.40', label: 'Ataşehir' },
  { prefix: '', label: 'Hepsi' },
];

const DynamicButtonFilters = ({ setFilter }) => {
  const [activePrefix, setActivePrefix] = useState('');

  const handleClick = (prefix) => {
    setActivePrefix(prefix);
    setFilter('muhatap_kod', prefix);
  };

  return (
    <div className="button-filters">
      {buttonFilters.map(filter => (
        <button
          key={filter.prefix}
          onClick={() => handleClick(filter.prefix)}
          className={`button-filters__button ${
            activePrefix === filter.prefix ? 'button-filters__button--active' : ''
          }`}
        >
          {filter.label}
        </button>
      ))}
    </div>
  );
};

DynamicButtonFilters.propTypes = {
  setFilter: PropTypes.func.isRequired,
};

export default DynamicButtonFilters;

