// frontend/src/components/ProductConfigv2/components/Configurator/FeatureDropdown.js

import React, { useState, useRef, useEffect } from 'react';
import PropTypes from 'prop-types';
import '../../styles/FeatureDropdown.css';

const FeatureDropdown = ({ feature, selectedOptionId, onOptionSelect }) => {
  const [isOpen, setIsOpen] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const dropdownRef = useRef(null);

  const options = feature.options || [];
  const filteredOptions = options.filter((opt) =>
    opt.name.toLowerCase().includes(searchTerm.toLowerCase())
  );

  // Dropdown dışına tıklanınca kapatmak için
  useEffect(() => {
    function handleClickOutside(e) {
      if (dropdownRef.current && !dropdownRef.current.contains(e.target)) {
        setIsOpen(false);
      }
    }
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const handleSelect = (optionId) => {
    onOptionSelect(optionId);
    setIsOpen(false); // seçince dropdown kapansın
  };

  // Seçili seçeneğin adını bul
  const selectedOptionName =
    options.find((opt) => opt.id === selectedOptionId)?.name || '';

  return (
    <div className="feature-dropdown" ref={dropdownRef}>
      <label className="feature-dropdown__label">{feature.name}</label>

      <div className="feature-dropdown__control" onClick={() => setIsOpen(!isOpen)}>
        <span className="feature-dropdown__selected">{selectedOptionName || 'Seçiniz...'}</span>
        <span className="feature-dropdown__arrow">▼</span>
      </div>

      {isOpen && (
        <div className="feature-dropdown__menu">
          {options.length > 5 && (
            <input
              type="text"
              className="feature-dropdown__search"
              placeholder="Ara..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
          )}
          <ul className="feature-dropdown__list">
            {/* Seçimi Temizle opsiyonu */}
            <li
              key="clear-selection"
              className="feature-dropdown__item feature-dropdown__item--clear"
              onClick={() => handleSelect(null)}
            >
              ❌ Seçimi Temizle
            </li>

            {filteredOptions.map((opt) => (
              <li
                key={opt.id}
                className={`feature-dropdown__item ${
                  opt.id === selectedOptionId ? 'feature-dropdown__item--active' : ''
                }`}
                onClick={() => handleSelect(opt.id)}
              >
                {opt.name}
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
};

FeatureDropdown.propTypes = {
  feature: PropTypes.shape({
    id: PropTypes.oneOfType([PropTypes.number, PropTypes.string]),
    name: PropTypes.string,
    options: PropTypes.arrayOf(
      PropTypes.shape({
        id: PropTypes.oneOfType([PropTypes.number, PropTypes.string]),
        name: PropTypes.string
      })
    )
  }).isRequired,
  selectedOptionId: PropTypes.oneOfType([PropTypes.string, PropTypes.number]),
  onOptionSelect: PropTypes.func.isRequired
};

FeatureDropdown.defaultProps = {
  selectedOptionId: null
};

export default FeatureDropdown;
