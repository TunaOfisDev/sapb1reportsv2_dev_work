// frontend/src/components/ProductConfigv2/components/Shared/OptionButton.js

import React from 'react';
import PropTypes from 'prop-types';
import '../../styles/OptionButton.css';

/**
 * OptionButton bileşeni, ürün konfigüratöründe her bir seçenek için tıklanabilir bir buton sunar.
 * Modern React 2025 standartlarına ve ERP görünümüne uygun tasarım dikkate alınarak oluşturulmuştur.
 *
 * Props:
 * - option: { id, name, price_delta, ... } şeklinde seçenek nesnesi.
 * - isActive: Bu seçeneğin aktif (seçilmiş) olup olmadığını belirten boolean.
 * - onClick: Seçenek tıklandığında çağrılan callback fonksiyonu (option.id parametresi ile).
 */
const OptionButton = ({ option, isActive, onClick }) => (
  <button
    type="button"
    className={`option-button ${isActive ? 'option-button--active' : ''}`}
    onClick={() => onClick(option.id)}
    aria-pressed={isActive}
  >
    {option.name}
  </button>
);

OptionButton.propTypes = {
  option: PropTypes.shape({
    id: PropTypes.oneOfType([PropTypes.number, PropTypes.string]).isRequired,
    name: PropTypes.string.isRequired,
    price_delta: PropTypes.oneOfType([PropTypes.number, PropTypes.string]),
  }).isRequired,
  isActive: PropTypes.bool,
  onClick: PropTypes.func.isRequired,
};

OptionButton.defaultProps = {
  isActive: false,
};

export default React.memo(OptionButton);
