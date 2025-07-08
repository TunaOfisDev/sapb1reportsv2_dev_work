// frontend/src/components/BomCostManager/components/FactorControl.js
import React, { useState, useEffect } from 'react';
import { increaseFactorValue, decreaseFactorValue, setFactorValue } from '../utils/factorValuePlus';
import { formatNumber } from '../utils/formatNumber';

/**
 * Faktör değerlerini artırıp azaltmaya yarayan kontrol bileşeni.
 * Artırma/azaltma butonları input alanının sağ tarafında küçük üçgen simgeler şeklinde yer alır.
 *
 * @param {Object} props - Bileşen props'ları
 * @param {number} props.value - Mevcut faktör değeri
 * @param {Function} props.onChange - Değer değiştiğinde çağrılacak fonksiyon
 * @param {string} props.label - Faktör etiketi
 * @param {number} props.step - Artış/Azalış adımı (varsayılan 0.05)
 * @returns {JSX.Element} Faktör kontrol bileşeni
 */
const FactorControl = ({ value, onChange, label, step = 0.05 }) => {
  const [displayValue, setDisplayValue] = useState('');
  const [isEditing, setIsEditing] = useState(false);

  useEffect(() => {
    if (!isEditing) {
      setDisplayValue(formatNumber(value, 2));
    }
  }, [value, isEditing]);

  const handleIncrease = () => {
    const newValue = increaseFactorValue(value, step);
    onChange(newValue);
  };

  const handleDecrease = () => {
    const newValue = decreaseFactorValue(value, step);
    onChange(newValue);
  };

  const handleFocus = () => {
    setIsEditing(true);
    setDisplayValue(value.toString());
  };

  const handleBlur = () => {
    setIsEditing(false);
    try {
      const processedValue = displayValue.replace(/\./g, '').replace(',', '.');
      const numericValue = parseFloat(processedValue);
      if (!isNaN(numericValue)) {
        const newValue = setFactorValue(numericValue);
        onChange(newValue);
      } else {
        setDisplayValue(formatNumber(value, 2));
      }
    } catch (error) {
      console.error("Sayı formatı hatası:", error);
      setDisplayValue(formatNumber(value, 2));
    }
  };

  const handleChange = (e) => {
    setDisplayValue(e.target.value);
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter') {
      e.target.blur();
    }
  };

  return (
    <div className="factor-control">
      <label className="factor-control__label">{label}:</label>
      <div className="factor-control__input-container">
        <input
          type="text"
          className="factor-control__input"
          value={displayValue}
          onChange={handleChange}
          onFocus={handleFocus}
          onBlur={handleBlur}
          onKeyDown={handleKeyDown}
        />
        <div className="factor-control__buttons">
          <button
            type="button"
            className="factor-control__button factor-control__button--up"
            onClick={handleIncrease}
            title="Artır"
          >
            &#9650;
          </button>
          <button
            type="button"
            className="factor-control__button factor-control__button--down"
            onClick={handleDecrease}
            title="Azalt"
          >
            &#9660;
          </button>
        </div>
      </div>
    </div>
  );
};

export default FactorControl;

