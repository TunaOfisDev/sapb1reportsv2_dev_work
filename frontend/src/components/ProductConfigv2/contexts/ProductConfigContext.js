// frontend/src/components/ProductConfigv2/contexts/ProductConfigContext.js

import React, { createContext, useContext, useState } from 'react';

/**
 * ProductConfigContext, ürün konfigürasyonuyla ilgili global state'i yönetmek için oluşturulmuştur.
 * Bu context üzerinden, seçili özellikler, toplam fiyat, kombinasyon geçerliliği ve hata bilgilerini paylaşabilirsin.
 */
const ProductConfigContext = createContext();

export const ProductConfigProvider = ({ children }) => {
  // Seçili özellikler: Örneğin, { featureId: optionId }
  const [selectedFeatures, setSelectedFeatures] = useState({});
  // Ürünün toplam fiyatı
  const [price, setPrice] = useState(0);
  // Kullanıcının seçtiği kombinasyonun geçerliliği (örneğin kural kontrolü sonucu)
  const [validCombination, setValidCombination] = useState(true);
  // Hata yönetimi için state (opsiyonel)
  const [error, setError] = useState(null);

  const contextValue = {
    selectedFeatures,
    setSelectedFeatures,
    price,
    setPrice,
    validCombination,
    setValidCombination,
    error,
    setError,
  };

  return (
    <ProductConfigContext.Provider value={contextValue}>
      {children}
    </ProductConfigContext.Provider>
  );
};

/**
 * useProductConfig hook'u, ProductConfigContext'e kolay erişim sağlar.
 * Bu hook'u, context içerisinde tanımlı tüm verileri ve setter fonksiyonlarını almak için kullanabilirsin.
 */
export const useProductConfig = () => {
  const context = useContext(ProductConfigContext);
  if (!context) {
    throw new Error('useProductConfig hook must be used within a ProductConfigProvider');
  }
  return context;
};

export default ProductConfigContext;
