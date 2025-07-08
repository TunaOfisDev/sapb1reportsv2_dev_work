// frontend/src/components/ProductConfigv2/api/configApi.js
import axiosInstance from '../../../api/axiosconfig';

const BASE_URL = 'productconfigv2'; // API'nin productconfigv2 bölümüne ait endpoint'ler

/**
 * Ürün ailelerini getirir.
 * Postman testinde; count, next, previous ve results array dönen yapı gözlemleniyor.
 */
export const getProductFamilies = () => {
  return axiosInstance.get(`${BASE_URL}/product-families/`);
};

/**
 * Ürün listesini getirir.
 * Postman verisinde; id, code, name, image, variant_code, variant_description, base_price, currency, variant_order, family gibi alanlar yer alıyor.
 * @param {Object} params - İsteğe bağlı sorgu parametreleri (ör. id, filtreler vb.)
 */
export const getProducts = (params) => {
  return axiosInstance.get(`${BASE_URL}/products/`, { params });
};

/**
 * Ürün özellik tipi listesini getirir.
 * Her özellik tipi; id, name, group, is_required, allow_multiple, variant_order, display_order, multiplier ve options (seçenek listesi) içeriyor.
 */
export const getSpecificationTypes = () => {
  return axiosInstance.get(`${BASE_URL}/specification-types/`);
};

/**
 * Ürün seçeneklerini (spec options) getirir.
 * Postman verisinde; id, name, variant_code, variant_description, image, price_delta, is_default, display_order alanları bulunuyor.
 */
export const getSpecOptions = () => {
  return axiosInstance.get(`${BASE_URL}/spec-options/`);
};

/**
 * Belirli bir ürüne ait özellikleri getirir.
 * Ürün spesifikasyonları; her biri ilgili spec_type ve options bilgilerini içeriyor.
 * @param {number|string} productId - Ürün ID'si.
 */
export const getProductSpecifications = (productId) => {
  return axiosInstance.get(`${BASE_URL}/product-specifications/`, {
    params: { product: productId }
  });
};

/**
 * Belirli bir ürüne ait varyantları getirir.
 * Varyantlar; id, code, fiyat, variant_order vb. alanları içerebilir.
 * @param {Object} params - İsteğe bağlı sorgu parametreleri.
 */
export const getVariants = (params) => {
  return axiosInstance.get(`${BASE_URL}/variants/`, { params });
};

/**
 * Kural listesini getirir.
 * Kural verileri; deny/allow gibi kural tipleri ile koşulları içerebilir.
 */
export const getRules = () => {
  return axiosInstance.get(`${BASE_URL}/rules/`);
};

/**
 * Yeni varyant oluşturur.
 * @param {Object} data - Oluşturulacak varyanta ait veriler.
 * Data içerisinde mutlaka "product_id" ve "selections" alanları bulunmalı.
 */
export const createVariant = (data) => {
  return axiosInstance.post(`${BASE_URL}/variants/create_from_selection/`, data);
};

/**
 * Ürün konfigürasyonu önizlemesi için seçilen verileri backend'e gönderir.
 * Postman'de konfigürasyon önizlemesi endpoint'i mevcutsa, bu fonksiyon backend'den geçerlilik ve güncel fiyat bilgisini döndürür.
 * @param {number|string} productId - Ürün ID'si.
 * @param {Object} data - Seçim verileri (ör. selections: { featureId: optionId, ... }).
 */
export const previewConfiguration = (productId, data) => {
  return axiosInstance.post(`${BASE_URL}/products/${productId}/configurator/preview/`, data);
};


/**
 * Belirli bir ürüne ait gruplanmış spesifikasyonları (özellik + opsiyonları) getirir.
 * Bu fonksiyon sadece ürünle ilişkilendirilmiş olanları döndürür.
 * @param {number|string} productId - Ürün ID'si.
 */
export const getGroupedProductSpecifications = (productId) => {
  return axiosInstance.get(`${BASE_URL}/products/${productId}/specifications-grouped/`);
};


export default {
  getProductFamilies,
  getProducts,
  getSpecificationTypes,
  getSpecOptions,
  getProductSpecifications,
  getGroupedProductSpecifications,
  getVariants,
  getRules,
  createVariant,
  previewConfiguration,
};
