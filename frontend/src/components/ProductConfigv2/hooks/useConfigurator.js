// frontend/src/components/ProductConfigv2/hooks/useConfigurator.js

import { useState, useEffect } from 'react';
import configApi from '../api/configApi';

const useConfigurator = (productId) => {
  const [product, setProduct] = useState(null);
  const [selectedFeatures, setSelectedFeatures] = useState({});
  const [price, setPrice] = useState(0);
  const [validCombination, setValidCombination] = useState(true);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // Ürün detaylarını ve özelliklerini API'den çeker
  const fetchProductConfiguration = async () => {
    setLoading(true);
    try {
      const numericId = parseInt(productId, 10);

      // 1) Ürün bilgilerini getir
      const productsResponse = await configApi.getProducts({ id: numericId });
      const foundProduct = productsResponse?.data?.results?.find((p) => p.id === numericId);

      if (!foundProduct) {
        throw new Error(`Ürün bulunamadı, id=${productId}`);
      }

      // 2) Yeni endpoint üzerinden sadece ürüne ait özellik + seçenekleri al
      const specResponse = await configApi.getGroupedProductSpecifications(numericId);
      const groupedSpecs = specResponse?.data || [];

      // 3) features alanına ata
      foundProduct.features = groupedSpecs;

      // 4) state'e yaz
      setProduct(foundProduct);
    } catch (err) {
      setError(err);
    } finally {
      setLoading(false);
    }
  };

  // Özellik seçimi
  const handleFeatureSelect = async (featureId, optionId) => {
    const newSelections = { ...selectedFeatures, [featureId]: optionId };
    setSelectedFeatures(newSelections);
    try {
      const previewResponse = await configApi.previewConfiguration(productId, { selections: newSelections });
      if (previewResponse.data) {
        setValidCombination(previewResponse.data.is_valid !== false);
        setPrice(previewResponse.data.preview_price || 0);
      }
    } catch (err) {
      setError(err);
    }
  };

  // Konfigürasyonu sıfırlamak için
  const resetConfiguration = () => {
    setSelectedFeatures({});
    setPrice(0);
    setValidCombination(true);
  };

  useEffect(() => {
    if (productId) {
      fetchProductConfiguration();
    }
  }, [productId]);

  return {
    product,
    selectedFeatures,
    price,
    validCombination,
    loading,
    error,
    handleFeatureSelect,
    resetConfiguration,
    setSelectedFeatures,
    fetchProductConfiguration,
  };
};

export default useConfigurator;
