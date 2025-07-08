// frontend/src/components/ProductConfigv2/components/Configurator/ProductVisualization.js

import React from 'react';
import PropTypes from 'prop-types';
import '../../styles/ProductVisualization.css';

/**
 * ProductVisualization bileşeni, ürün konfigüratöründe
 * ürünün görsel önizlemesini sağlar. Seçili özelliklere bağlı olarak
 * dinamik bir görsel URL oluşturabilir.
 *
 * Modern React 2025 standartlarına uygun olarak fonksiyonel bileşen, 
 * performans optimizasyonu (React.memo) ve erişilebilirlik dikkate alınarak tasarlanmıştır.
 *
 * Props:
 * - product: Ürün bilgilerini içeren nesne (ör. { id, name, image }).
 * - selectedFeatures: Kullanıcı tarafından seçilen özellikler nesnesi (ör. { color: 'red', ... }).
 */
const ProductVisualization = ({ product, selectedFeatures }) => {
  /**
   * Seçili özelliklere göre ürün görsel URL'sini oluşturur.
   * Örneğin, eğer ürün resmi dinamik olarak renk bazında değişiyorsa,
   * seçili renk bilgisine göre URL'yi günceller.
   *
   * @returns {string} Oluşturulmuş görsel URL'si.
   */
  const getImageUrl = () => {
    if (product && product.image) {
      let baseUrl = product.image;
      // Örnek: Seçili özellikler arasında "color" varsa, URL'ye ekleme yapalım.
      if (selectedFeatures && selectedFeatures.color) {
        // Örneğin; "product.jpg" -> "product_red.jpg"
        const dotIndex = baseUrl.lastIndexOf('.');
        if (dotIndex !== -1) {
          const namePart = baseUrl.substring(0, dotIndex);
          const extension = baseUrl.substring(dotIndex);
          return `${namePart}_${selectedFeatures.color}${extension}`;
        }
      }
      return baseUrl;
    }
    // Ürün resmi yoksa varsayılan bir görsel döndür.
    return '/assets/images/default-product.png';
  };

  return (
    <div className="product-visualization">
      <img 
        src={getImageUrl()} 
        alt={product ? product.name : 'Ürün Görseli'} 
        className="product-visualization__image"
      />
    </div>
  );
};

ProductVisualization.propTypes = {
  product: PropTypes.shape({
    id: PropTypes.oneOfType([PropTypes.number, PropTypes.string]),
    name: PropTypes.string,
    image: PropTypes.string,
  }),
  selectedFeatures: PropTypes.object,
};

ProductVisualization.defaultProps = {
  product: null,
  selectedFeatures: {},
};

export default React.memo(ProductVisualization);
