// frontend/src/components/TunaInsSupplierPayment/utils/DynamicButtonFilters.js
import React from 'react';
import PropTypes from 'prop-types';
import '../css/DynamicButtonFilters.css';

const buttonFilters = [
  { prefix: '320.14', label: 'Hadımköy' },
  { prefix: '320.40', label: 'Ataşehir' },
  { prefix: '', label: 'Hepsi' },
];

const DynamicButtonFilters = ({ setFilter }) => {
  return (
    <div className="button-filters">
      {buttonFilters.map(filter => (
        <button
          key={filter.prefix}
          onClick={() => setFilter('cari_kod', filter.prefix)}
          className="button-filters__button"
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
