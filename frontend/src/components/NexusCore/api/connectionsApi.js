// path: frontend/src/components/NexusCore/api/connectionsApi.js

import axiosInstance from '../../../api/axiosconfig';

// ### DÜZELTME: API kök yolunun sonunda slash olmamalıdır. ###
const API_ENDPOINT = 'nexuscore/connections';

/**
 * Tüm veri tabanı bağlantılarını listeler.
 */
export const getConnections = async () => {
  try {
    // Liste endpoint'i için slash'ı burada ekliyoruz.
    const response = await axiosInstance.get(`${API_ENDPOINT}/`);
    return response.data;
  } catch (error) {
    console.error("Veri bağlantıları alınırken hata oluştu:", error);
    throw error;
  }
};

/**
 * Belirli bir ID'ye sahip veri tabanı bağlantısının detaylarını getirir.
 */
export const getConnectionById = async (id) => {
  try {
    // Detay endpoint'i /1/ şeklinde oluşur.
    const response = await axiosInstance.get(`${API_ENDPOINT}/${id}/`);
    return response.data;
  } catch (error) {
    console.error(`ID'si ${id} olan bağlantı alınırken hata:`, error);
    throw error;
  }
};

/**
 * Yeni bir veri tabanı bağlantısı oluşturur.
 */
export const createConnection = async (connectionData) => {
  try {
    // Create endpoint'i de liste endpoint'i ile aynıdır.
    const response = await axiosInstance.post(`${API_ENDPOINT}/`, connectionData);
    return response.data;
  } catch (error) {
    console.error("Yeni bağlantı oluşturulurken hata:", error);
    throw error;
  }
};

/**
 * Mevcut bir veri tabanı bağlantısını günceller.
 */
export const updateConnection = async (id, connectionData) => {
  try {
    const response = await axiosInstance.patch(`${API_ENDPOINT}/${id}/`, connectionData);
    return response.data;
  } catch (error) {
    console.error(`ID'si ${id} olan bağlantı güncellenirken hata:`, error);
    throw error;
  }
};

/**
 * Bir veri tabanı bağlantısını siler.
 */
export const deleteConnection = async (id) => {
  try {
    await axiosInstance.delete(`${API_ENDPOINT}/${id}/`);
  } catch (error) {
    console.error(`ID'si ${id} olan bağlantı silinirken hata:`, error);
    throw error;
  }
};

/**
 * Bir veri tabanı bağlantısını test etmek için backend'deki özel action'ı tetikler.
 */
export const testConnection = async (id) => {
    try {
        // Özel action yolu: /1/test_connection/
        const response = await axiosInstance.post(`${API_ENDPOINT}/${id}/test_connection/`);
        return response.data;
    } catch (error) {
        console.error(`ID'si ${id} olan bağlantı test edilirken hata:`, error);
        throw error;
    }
};