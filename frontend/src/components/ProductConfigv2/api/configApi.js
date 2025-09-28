// frontend/src/components/ProductConfigv2/api/configApi.js
import axiosInstance from '../../../api/axiosconfig';

const BASE_URL = 'productconfigv2'; // API'nin productconfigv2 bölümüne ait endpoint'ler

/**
 * Ürün ailelerini getirir.
 */
export const getProductFamilies = () => {
  return axiosInstance.get(`${BASE_URL}/product-families/`);
};

/**
 * Ürün listesini getirir.
 * @param {Object} params - İsteğe bağlı sorgu parametreleri (ör. id, filtreler vb.)
 */
export const getProducts = (params) => {
  return axiosInstance.get(`${BASE_URL}/products/`, { params });
};

/**
 * Verilen ID'ye göre tek bir ürünün detaylarını getirir.
 * @param {number|string} productId - Ürün ID'si.
 */
export const getProductById = (productId) => {
  return axiosInstance.get(`${BASE_URL}/products/${productId}/`);
};

/**
 * Ürün özellik tipi listesini getirir.
 */
export const getSpecificationTypes = () => {
  return axiosInstance.get(`${BASE_URL}/specification-types/`);
};

/**
 * Ürün seçeneklerini (spec options) getirir.
 */
export const getSpecOptions = () => {
  return axiosInstance.get(`${BASE_URL}/spec-options/`);
};

/**
 * Belirli bir ürüne ait özellikleri getirir.
 * @param {number|string} productId - Ürün ID'si.
 */
export const getProductSpecifications = (productId) => {
  return axiosInstance.get(`${BASE_URL}/product-specifications/`, {
    params: { product: productId }
  });
};

/**
 * Belirli bir ürüne ait varyantları getirir.
 * @param {Object} params - İsteğe bağlı sorgu parametreleri.
 */
export const getVariants = (params) => {
  return axiosInstance.get(`${BASE_URL}/variants/`, { params });
};

/**
 * Kural listesini getirir.
 */
export const getRules = () => {
  return axiosInstance.get(`${BASE_URL}/rules/`);
};

/**
 * GÜNCELLENDİ: Yeni varyant oluşturur.
 * @param {Object} data - Oluşturulacak varyanta ait veriler.
 * Data içerisinde "product_id", "selections" ve "project_name" alanları bulunmalıdır.
 */
export const createVariant = (data) => {
  return axiosInstance.post(`${BASE_URL}/variants/create_from_selection/`, data);
};

/**
 * GÜNCELLENDİ: Ürün konfigürasyonu önizlemesi için seçilen verileri backend'e gönderir.
 * Artık /variants/preview/ endpoint'ini kullanır ve tek bir data objesi alır.
 * @param {Object} data - { product_id: number, selections: { featureId: optionId, ... } }
 */
export const previewConfiguration = (data) => {
  return axiosInstance.post(`${BASE_URL}/variants/preview/`, data);
};

/**
 * Belirli bir ürüne ait gruplanmış spesifikasyonları (özellik + opsiyonları) getirir.
 * Bu fonksiyon sadece ürünle ilişkilendirilmiş olanları döndürür.
 * @param {number|string} productId - Ürün ID'si.
 */
export const getGroupedProductSpecifications = (productId) => {
  return axiosInstance.get(`${BASE_URL}/products/${productId}/specifications-grouped/`);
};

/**
 * Verilen bir referans kodu (55'li kod) ile Django backend'i üzerinden
 * SAP'den canlı fiyat sorgusu yapar.
 * @param {string} referenceCode - Fiyatı sorgulanacak 55'li kod.
 */
export const getSapPrice = (referenceCode) => {
  return axiosInstance.get(`${BASE_URL}/variants/get-sap-price/`, {
    params: { reference_code: referenceCode }
  });
};


/**
 * Veritabanında kayıtlı bir varyantın fiyatını SAP'den çekip günceller.
 * @param {number|string} variantId - Fiyatı güncellenecek varyantın ID'si.
 */
export const updateVariantPriceFromSap = (variantId) => {
  return axiosInstance.post(`${BASE_URL}/variants/${variantId}/update-price-from-sap/`);
};


export default {
  getProductFamilies,
  getProducts,
  getProductById,
  getSpecificationTypes,
  getSpecOptions,
  getProductSpecifications,
  getGroupedProductSpecifications,
  getVariants,
  getRules,
  createVariant,
  previewConfiguration,
  getSapPrice,
  updateVariantPriceFromSap,
};