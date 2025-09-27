// frontend/src/components/StockCardIntegration/api/productPriceListApi.js
import axiosInstance from '../../../api/axiosconfig';

/**
 * Ürün fiyat listesi – canlı veriyi getirir (GET /product-price-list/live/)
 */
export const fetchLiveProductPriceList = async () => {
  const response = await axiosInstance.get('stockcardintegration/product-price-list/live/');
  return response.data;
};

/**
 * Ürün fiyat listesi – manuel senkronize et (POST /product-price-list/refresh/)
 */
export const refreshProductPriceList = async () => {
  const response = await axiosInstance.post('stockcardintegration/product-price-list/refresh/');
  return response.data;
};

/**
 * Ürün fiyat listesi – tam liste (DB'deki kayıtlar) (GET /product-price-list/)
 */
export const fetchAllProductPriceList = async (params = {}) => {
  const response = await axiosInstance.get('stockcardintegration/product-price-list/', { params });
  return response.data;
};

/**
 * Ürün fiyat listesi – tek kayıt detayı (GET /product-price-list/:id/)
 */
export const fetchProductPriceById = async (id) => {
  const response = await axiosInstance.get(`stockcardintegration/product-price-list/${id}/`);
  return response.data;
};

/**
 * Ürün fiyat listesi – yeni kayıt oluştur (POST /product-price-list/)
 */
export const createProductPrice = async (payload) => {
  const response = await axiosInstance.post('stockcardintegration/product-price-list/', payload);
  return response.data;
};

/**
 * Ürün fiyat listesi – mevcut kaydı güncelle (PUT /product-price-list/:id/)
 */
export const updateProductPrice = async (id, payload) => {
  const response = await axiosInstance.put(`stockcardintegration/product-price-list/${id}/`, payload);
  return response.data;
};

/**
 * Ürün fiyat listesi – toplu kayıt gönderimi (POST /product-price-list/)
 */
export const bulkUpsertProductPrices = async (payloadList) => {
  const response = await axiosInstance.post('stockcardintegration/product-price-list/', payloadList);
  return response.data;
};
