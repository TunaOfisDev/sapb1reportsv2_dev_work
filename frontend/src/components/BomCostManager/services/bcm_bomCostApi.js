// frontend/src/components/BomCostManager/services/bcm_bomCostApi.js

import axiosInstance from '../../../api/axiosconfig';

const BASE_URL = '/bomcostmanager';

/**
 * BOM ürün listesini getirir.
 */
export const fetchBomProducts = async () => {
    try {
        const response = await axiosInstance.get(`${BASE_URL}/bomproducts/`);
        return response.data;
    } catch (error) {
        console.error('BOM ürünleri alınırken hata oluştu:', error);
        throw error;
    }
};

/**
 * SAP HANA'dan BOM ürün verisini getirir ve yerel veritabanına kaydeder.
 */
export const fetchBomProductsFromHana = async () => {
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
export const fetchBomProductDetails = async (itemCode) => {
    try {
        const response = await axiosInstance.get(`${BASE_URL}/bomproducts/${itemCode}/`);
        return response.data;
    } catch (error) {
        console.error(`BOM ürünü (${itemCode}) alınırken hata oluştu:`, error);
        throw error;
    }
};

/**
 * BOM bileşen listesini getirir.
 */
export const fetchBomComponents = async (itemCode) => {
    try {
        const response = await axiosInstance.get(`/hanadbcon/query/bomcomponent/`, {
            params: { item_code: itemCode }
        });
        return response.data;
    } catch (error) {
        console.error(`BOM bileşenleri (${itemCode}) alınırken hata oluştu:`, error);
        throw error;
    }
};

/**
 * SAP HANA'dan belirli bir ürünün BOM bileşenlerini getirir.
 * @param {string} itemCode - Ürün kodu
 */
export const fetchBomComponentsFromHana = async (itemCode) => {
    try {
        const response = await axiosInstance.post(`${BASE_URL}/bomcomponents/fetch/`, null, {
            params: { item_code: itemCode }
        });
        return response.data;
    } catch (error) {
        console.error(`SAP HANA'dan BOM bileşenleri (${itemCode}) alınırken hata oluştu:`, error);
        throw error;
    }
};

/**
 * Belirli bir BOM bileşenini günceller (override fiyat veya çarpanlar).
 * @param {string} componentId - Güncellenecek bileşen ID'si
 * @param {Object} updatedData - Güncellenmiş veriler
 */
export const updateBomComponent = async (componentId, updatedData) => {
    try {
        const response = await axiosInstance.put(`${BASE_URL}/bomcomponents/${componentId}/`, updatedData);
        return response.data;
    } catch (error) {
        console.error(`BOM bileşeni (${componentId}) güncellenirken hata oluştu:`, error);
        throw error;
    }
};
