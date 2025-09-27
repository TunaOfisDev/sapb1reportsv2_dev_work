// frontend/src/components/ProductConfigv2/components/Shared/FeatureCard.js
import React from 'react';
import PropTypes from 'prop-types';
import '../../styles/FeatureCard.css';

/**
 * FeatureCard bileşeni, ürün özelliklerini temsil eden kart yapısıdır.
 * Modern React (2025) standartları göz önünde bulundurularak, erişilebilirlik (accessibility)
 * ve performans optimizasyonları (örn. memoization) dikkate alınarak oluşturulmuştur.
 *
 * Props:
 * - feature: { id, name, description, image } nesnesi
 * - isSelected: Bu kartın seçili olup olmadığını belirten boolean değer
 * - onClick: Kart tıklandığında çalışacak callback fonksiyonu (feature id'si parametre olarak gönderilir)
 */
const FeatureCard = ({ feature, isSelected, onClick }) => {
  const handleKeyPress = (e) => {
    if (e.key === 'Enter' || e.key === ' ') {
      onClick(feature.id);
    }
  };

  return (
    <div
      className={`feature-card ${isSelected ? 'feature-card--selected' : ''}`}
      role="button"
      tabIndex={0}
      onClick={() => onClick(feature.id)}
      onKeyPress={handleKeyPress}
    >
      {feature.image && (
        <img
          src={feature.image}
          alt={feature.name}
          className="feature-card__image"
        />
      )}
      <div className="feature-card__content">
        <h3 className="feature-card__title">{feature.name}</h3>
        {feature.description && (
          <p className="feature-card__description">{feature.description}</p>
        )}
      </div>
    </div>
  );
};

FeatureCard.propTypes = {
  feature: PropTypes.shape({
    id: PropTypes.oneOfType([PropTypes.number, PropTypes.string]).isRequired,
    name: PropTypes.string.isRequired,
    description: PropTypes.string,
    image: PropTypes.string,
  }).isRequired,
  isSelected: PropTypes.bool,
  onClick: PropTypes.func.isRequired,
};

FeatureCard.defaultProps = {
  isSelected: false,
};

export default React.memo(FeatureCard);
