// frontend/src/components/ProductConfigv2/components/Admin/ProductManager.js

import React, { useState, useEffect } from 'react';
import PropTypes from 'prop-types';
import configApi from '../../api/configApi';
import '../../styles/ProductManager.css';

/**
 * ProductManager bileşeni, admin panelinde ürün bilgilerini oluşturma veya düzenleme
 * işlemlerini gerçekleştirir. Eğer bir productId sağlanırsa, ilgili ürünün bilgileri yüklenir
 * ve düzenleme modunda çalışır; aksi halde yeni ürün oluşturulur.
 *
 * Modern React 2025 standartlarına uygun olarak, fonksiyonel bileşen, hook'lar ve erişilebilirlik
 * prensipleri dikkate alınarak oluşturulmuştur.
 *
 * Props:
 * - productId: Düzenlenecek ürünün ID'si (opsiyonel).
 * - onProductSaved: Ürün başarıyla kaydedildiğinde çağrılan callback fonksiyonu.
 */
const ProductManager = ({ productId, onProductSaved }) => {
  const [product, setProduct] = useState({
    name: '',
    description: '',
    base_price: '',
    currency: '',
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // Eğer productId mevcutsa, ürün bilgilerini API'den çek
  useEffect(() => {
    if (productId) {
      setLoading(true);
      configApi.getProducts({ id: productId })
        .then((response) => {
          if (response.data.results && response.data.results.length > 0) {
            setProduct(response.data.results[0]);
          }
        })
        .catch((err) => setError(err))
        .finally(() => setLoading(false));
    }
  }, [productId]);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setProduct((prev) => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      if (productId) {
        // Ürün güncelleme
        await configApi.updateProduct(productId, product);
      } else {
        // Yeni ürün oluşturma
        await configApi.createProduct(product);
      }
      if (onProductSaved) {
        onProductSaved();
      }
    } catch (err) {
      setError(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="product-manager">
      <h2>{productId ? 'Ürünü Düzenle' : 'Yeni Ürün Oluştur'}</h2>
      {error && <div className="product-manager__error">Hata: {error.message}</div>}
      {loading ? (
        <div className="product-manager__loading">Yükleniyor...</div>
      ) : (
        <form className="product-manager__form" onSubmit={handleSubmit}>
          <div className="form-group">
            <label htmlFor="name">Ürün Adı</label>
            <input
              type="text"
              id="name"
              name="name"
              value={product.name}
              onChange={handleChange}
              required
            />
          </div>
          <div className="form-group">
            <label htmlFor="description">Açıklama</label>
            <textarea
              id="description"
              name="description"
              value={product.description}
              onChange={handleChange}
            />
          </div>
          <div className="form-group">
            <label htmlFor="base_price">Temel Fiyat</label>
            <input
              type="number"
              id="base_price"
              name="base_price"
              value={product.base_price}
              onChange={handleChange}
              required
            />
          </div>
          <div className="form-group">
            <label htmlFor="currency">Para Birimi</label>
            <input
              type="text"
              id="currency"
              name="currency"
              value={product.currency}
              onChange={handleChange}
              required
            />
          </div>
          <button type="submit" className="product-manager__submit">
            {productId ? 'Güncelle' : 'Oluştur'}
          </button>
        </form>
      )}
    </div>
  );
};

ProductManager.propTypes = {
  productId: PropTypes.oneOfType([PropTypes.number, PropTypes.string]),
  onProductSaved: PropTypes.func,
};

ProductManager.defaultProps = {
  productId: null,
  onProductSaved: null,
};

export default ProductManager;
