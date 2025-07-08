// frontend/src/components/SupplierPayment/utils/DynamicButtonFilters.js
import React from 'react';
import PropTypes from 'prop-types';
import '../css/DynamicButtonFilters.css';

const buttonFilters = [
  { prefix: '320.01', label: 'Fabrika' },
  { prefix: '320.06', label: 'Elektrik Su'},
  { prefix: '320.14', label: 'Hadımköy' },
  { prefix: '320.40', label: 'Ataşehir' },
  { prefix: '320.90', label: 'İthalat' },
  { prefix: '320.11', label: 'Diğer' },
  { prefix: '320.50', label: 'Pasif' },
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
