// frontend/src/components/ProductConfigv2/components/Shared/ProductCard.js
import React from 'react';
import PropTypes from 'prop-types';
import '../../styles/ProductCard.css';

/**
 * ProductCard bileşeni, ürünün temel bilgilerini içeren bir kart yapısı sunar.
 * Bu bileşen, ürün görseli, isim, açıklama ve fiyat bilgilerini gösterir.
 * Modern React 2025 standartları, erişilebilirlik ve performans optimizasyonları göz önünde bulundurularak tasarlanmıştır.
 *
 * Props:
 * - product: Ürün detaylarını içeren nesne (ör. { id, name, description, image, base_price, currency }).
 * - onClick: Kart tıklandığında çalışacak callback fonksiyonu (ürün id'si parametresiyle çağrılır).
 */
const ProductCard = ({ product, onClick }) => {
  const handleKeyPress = (e) => {
    if (e.key === 'Enter' || e.key === ' ') {
      onClick(product.id);
    }
  };

  return (
    <div
      className="product-card"
      role="button"
      tabIndex={0}
      onClick={() => onClick(product.id)}
      onKeyPress={handleKeyPress}
    >
      {product.image && (
        <img
          src={product.image}
          alt={product.name}
          className="product-card__image"
        />
      )}
      <div className="product-card__content">
        <h2 className="product-card__title">{product.name}</h2>
        {product.description && (
          <p className="product-card__description">{product.description}</p>
        )}
        {product.base_price && (
          <p className="product-card__price">
            {product.currency ? `${product.currency} ` : ''}{product.base_price}
          </p>
        )}
      </div>
    </div>
  );
};

ProductCard.propTypes = {
  product: PropTypes.shape({
    id: PropTypes.oneOfType([PropTypes.number, PropTypes.string]).isRequired,
    name: PropTypes.string.isRequired,
    description: PropTypes.string,
    image: PropTypes.string,
    base_price: PropTypes.oneOfType([PropTypes.number, PropTypes.string]),
    currency: PropTypes.string,
  }).isRequired,
  onClick: PropTypes.func.isRequired,
};

export default React.memo(ProductCard);
