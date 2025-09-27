// frontend/src/components/ProductConfigv2/hooks/useConfigurator.js

import { useState, useEffect, useCallback } from 'react';
import configApi from '../api/configApi';

const useConfigurator = (productId) => {
  const [product, setProduct] = useState(null);
  const [selectedFeatures, setSelectedFeatures] = useState({});
  const [price, setPrice] = useState(null);
  const [validCombination, setValidCombination] = useState(true);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [projectName, setProjectName] = useState('');
  const [referenceCode, setReferenceCode] = useState('');
  const [priceLoading, setPriceLoading] = useState(false);
  const [priceError, setPriceError] = useState(null);

  const fetchProductConfiguration = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const numericId = parseInt(productId, 10);

      // 1) Yeni, direkt fonksiyonu kullanarak ürünü getir.
      const productResponse = await configApi.getProductById(numericId);
      const foundProduct = productResponse.data;

      if (!foundProduct) {
        throw new Error(`Ürün bulunamadı, id=${productId}`);
      }

      // 2) Ürüne ait özellikleri ve seçenekleri al (bu kısım aynı).
      const specResponse = await configApi.getGroupedProductSpecifications(numericId);
      foundProduct.features = specResponse?.data || [];

      // 3) state'e yaz
      setProduct(foundProduct);
      setPrice(foundProduct.base_price || 0);
    } catch (err) {
      // API'den 404 hatası gelirse, bu blok çalışacak.
      console.error("Ürün konfigürasyonu alınırken hata:", err);
      setError(new Error("Ürün bulunamadı veya yüklenirken bir hata oluştu."));
    } finally {
      setLoading(false);
    }
  }, [productId]);

  // GÜNCELLEME: Bu fonksiyon artık dışarıdan çağrılacak
  const fetchPriceFromSap = useCallback(async () => {
    if (!referenceCode) {
      setPriceError("Fiyat sorgulamak için önce bir referans kodu oluşturulmalıdır.");
      return;
    }
    setPriceLoading(true);
    setPriceError(null);
    try {
      const response = await configApi.getSapPrice(referenceCode);
      setPrice(response.data.price);
    } catch (error) {
      console.error("SAP fiyatı alınamadı:", error);
      setPrice(null); // Hata durumunda fiyatı null yap
      setPriceError("SAP'den fiyat bilgisi alınamadı.");
    } finally {
      setPriceLoading(false);
    }
  }, [referenceCode]);

  // KALDIRILDI: referenceCode değiştiğinde otomatik fiyat çeken useEffect kaldırıldı.

  const handleFeatureSelect = async (featureId, optionId) => {
    const newSelections = { ...selectedFeatures, [featureId]: optionId };
    setSelectedFeatures(newSelections);
    setPrice(null);
    setPriceError(null);

    try {
      const payload = { product_id: productId, selections: newSelections };
      const previewResponse = await configApi.previewConfiguration(payload);
      if (previewResponse.data) {
        setValidCombination(previewResponse.data.is_valid !== false);
        setReferenceCode(previewResponse.data.reference_code_55 || '');
      }
    } catch (err) {
      setError(err);
      setReferenceCode('');
    }
  };

  const resetConfiguration = () => {
    setSelectedFeatures({});
    setPrice(product?.base_price || null);
    setValidCombination(true);
    setProjectName('');
    setReferenceCode('');
    setPriceError(null);
    setError(null);
  }

  useEffect(() => {
    if (productId) {
      fetchProductConfiguration();
    }
  }, [productId, fetchProductConfiguration]);

  // GÜNCELLEME: Yeni state'leri ve manuel tetikleme fonksiyonunu dışarıya aç
  return {
    product,
    selectedFeatures,
    price,
    validCombination,
    loading,
    error,
    projectName,
    setProjectName,
    referenceCode,
    priceLoading,
    priceError,
    handleFeatureSelect,
    resetConfiguration,
    fetchPriceFromSap,
  };
};

export default useConfigurator;