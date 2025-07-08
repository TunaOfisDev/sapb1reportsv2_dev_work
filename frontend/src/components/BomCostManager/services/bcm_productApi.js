// frontend/src/components/BomCostManager/services/bcm_productApi.js

import axiosInstance from '../../../api/axiosconfig';

const BASE_URL = '/bomcostmanager';

/**
 * Tüm BOM ürünlerini getirir.
 */
export const fetchAllProducts = async () => {
    try {
        const response = await axiosInstance.get(`${BASE_URL}/bomproducts/`);
        return response.data;
    } catch (error) {
        console.error('BOM ürünleri alınırken hata oluştu:', error);
        throw error;
    }
};

/**
 * SAP HANA'dan BOM ürün verilerini getirir ve yerel veritabanına kaydeder.
 */
export const fetchProductsFromHana = async () => {
    try {
        const response = await axiosInstance.post(`${BASE_URL}/bomproducts/fetch/`);
        return response.data;
    } catch (error) {
        console.error('SAP HANA dan BOM ürünleri alınırken hata oluştu:', error);
        throw error;
    }
};

/**
 * Belirli bir BOM ürününün detaylarını getirir.
 * @param {string} itemCode - Ürün kodu
 */
export const fetchProductDetails = async (itemCode) => {
    try {
        const response = await axiosInstance.get(`${BASE_URL}/bomproducts/${itemCode}/`);
        return response.data;
    } catch (error) {
        console.error(`BOM ürünü (${itemCode}) alınırken hata oluştu:`, error);
        throw error;
    }
};

/**
 * Yerel veritabanındaki BOM ürünlerinin son güncelleme zamanını getirir.
 */
export const fetchLastUpdatedTime = async () => {
    try {
        const response = await axiosInstance.get(`${BASE_URL}/bomproducts/last-updated/`);
        return response.data;
    } catch (error) {
        console.error('BOM ürünlerinin son güncelleme zamanı alınırken hata oluştu:', error);
        throw error;
    }
};
