// path: frontend/src/components/StockCardIntegration/components/CurrencyInput.jsx

import { useState, useRef } from 'react';
import PropTypes from 'prop-types';

const CurrencyInput = ({ value, onChange, decimalPlaces = 4, ...props }) => {
  const [displayValue, setDisplayValue] = useState(value ? value.toString().replace('.', ',') : '');
  const inputRef = useRef(null);

  const handleChange = (e) => {
    let input = e.target.value;

    // Sadece sayılar ve virgül
    input = input.replace(/[^0-9,]/g, '');

    // Virgül sonrası decimalPlaces kadar basamakla sınırla
    const parts = input.split(',');
    if (parts[1] && parts[1].length > decimalPlaces) {
      parts[1] = parts[1].slice(0, decimalPlaces);
      input = parts.join(',');
    }

    // Maksimum uzunluk kontrolü (13 tam + 1 virgül + 4 ondalık = 18 karakter)
    if (input.replace(',', '').length > 17) {
      return; // Fazla uzun, değişiklik yapma
    }

    setDisplayValue(input);

    // Sayısal değere çevir (SAP HANA için)
    const numericValue = input ? parseFloat(input.replace(',', '.')) : '';
    onChange(isNaN(numericValue) ? '' : numericValue);
  };

  const handleKeyDown = (e) => {
    // Virgül sonrası fazla basamak engelle
    const parts = e.target.value.split(',');
    if (e.key !== 'Backspace' && parts[1] && parts[1].length >= decimalPlaces && inputRef.current.selectionStart > parts[0].length) {
      e.preventDefault();
    }
  };

  return (
    <input
      ref={inputRef}
      {...props}
      value={displayValue}
      onChange={handleChange}
      onKeyDown={handleKeyDown}
      inputMode="decimal"
      placeholder={`0,${'0'.repeat(decimalPlaces)}`}
      aria-label="Para miktarı girişi"
      style={{ textAlign: 'right', ...props.style }}
    />
  );
};

CurrencyInput.propTypes = {
  value: PropTypes.oneOfType([PropTypes.string, PropTypes.number]),
  onChange: PropTypes.func.isRequired,
  decimalPlaces: PropTypes.number,
};

export default CurrencyInput;
