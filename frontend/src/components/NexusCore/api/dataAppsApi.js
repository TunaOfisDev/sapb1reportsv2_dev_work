// path: frontend/src/components/NexusCore/api/dataAppsApi.js

import axiosInstance from '../../../api/axiosconfig';

// Backend'deki DataAppViewSet'in ana yolu
const API_ENDPOINT = 'nexuscore/data-apps/';

/**
 * Kullanıcının görmeye yetkili olduğu tüm Veri Uygulamalarını listeler.
 */
export const getDataApps = async () => {
  try {
    const response = await axiosInstance.get(API_ENDPOINT);
    return response.data;
  } catch (error) {
    console.error("Veri Uygulamaları alınırken hata oluştu:", error);
    throw error;
  }
};

/**
 * Belirli bir ID'ye sahip Veri Uygulamasının detaylarını getirir.
 * (Tabloları ve ilişkileri de nested olarak getirir)
 */
export const getDataAppById = async (id) => {
  try {
    const response = await axiosInstance.get(`${API_ENDPOINT}${id}/`);
    return response.data;
  } catch (error) {
    console.error(`ID'si ${id} olan Veri Uygulaması alınırken hata:`, error);
    throw error;
  }
};

/**
 * Yeni bir Veri Uygulaması (veri modeli) oluşturur.
 * @param {object} appData - { title, description, connection_id, virtual_tables: [id1, id2], sharing_status }
 */
export const createDataApp = async (appData) => {
  try {
    const response = await axiosInstance.post(API_ENDPOINT, appData);
    return response.data;
  } catch (error) {
    console.error("Yeni Veri Uygulaması oluşturulurken hata:", error);
    throw error;
  }
};

/**
 * Mevcut bir Veri Uygulamasını günceller.
 */
export const updateDataApp = async (id, appData) => {
  try {
    // PATCH kullanmak, sadece değişen alanları göndermemizi sağlar.
    const response = await axiosInstance.patch(`${API_ENDPOINT}${id}/`, appData);
    return response.data;
  } catch (error) {
    console.error(`ID'si ${id} olan Veri Uygulaması güncellenirken hata:`, error);
    throw error;
  }
};

/**
 * Bir Veri Uygulamasını siler. (Buna bağlı Rapor Şablonları SET_NULL olacaktır).
 */
export const deleteDataApp = async (id) => {
  try {
    await axiosInstance.delete(`${API_ENDPOINT}${id}/`);
  } catch (error) {
    console.error(`ID'si ${id} olan Veri Uygulaması silinirken hata:`, error);
    throw error;
  }
};