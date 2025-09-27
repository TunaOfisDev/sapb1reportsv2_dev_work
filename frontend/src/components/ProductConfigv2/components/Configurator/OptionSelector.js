// frontend/src/components/ProductConfigv2/components/Configurator/OptionSelector.js

import React from 'react';
import PropTypes from 'prop-types';
import OptionButton from '../Shared/OptionButton';
import '../../styles/OptionSelector.css';

/**
 * OptionSelector bileşeni, belirli bir özellik için mevcut seçenekleri 
 * listeleyen ve kullanıcı seçimini yöneten bir kapsayıcıdır.
 * 
 * Modern React 2025 standartlarına uygun olarak, erişilebilirlik ve 
 * performans optimizasyonları (React.memo) dikkate alınarak oluşturulmuştur.
 *
 * Props:
 * - options: Seçenek nesnelerinin dizisi (ör. [{ id, name, price_delta }, ...]).
 * - selectedOption: Şu anda seçili olan seçenek ID'si.
 * - onSelect: Seçenek tıklandığında çağrılan callback fonksiyonu (seçenek ID'sini parametre olarak alır).
 * - title: (Opsiyonel) Seçenek grubunun başlığı.
 */
const OptionSelector = ({ options, selectedOption, onSelect, title }) => {
  return (
    <div className="option-selector">
      {title && <h3 className="option-selector__title">{title}</h3>}
      <div className="option-selector__buttons">
        {options.map((option) => (
          <OptionButton
            key={option.id}
            option={option}
            isActive={selectedOption === option.id}
            onClick={onSelect}
          />
        ))}
      </div>
    </div>
  );
};

OptionSelector.propTypes = {
  options: PropTypes.arrayOf(
    PropTypes.shape({
      id: PropTypes.oneOfType([PropTypes.string, PropTypes.number]).isRequired,
      name: PropTypes.string.isRequired,
      price_delta: PropTypes.oneOfType([PropTypes.string, PropTypes.number]),
    })
  ).isRequired,
  selectedOption: PropTypes.oneOfType([PropTypes.string, PropTypes.number]),
  onSelect: PropTypes.func.isRequired,
  title: PropTypes.string,
};

OptionSelector.defaultProps = {
  selectedOption: null,
  title: '',
};

export default React.memo(OptionSelector);
