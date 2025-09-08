// path: frontend/src/components/NexusCore/api/appRelationshipsApi.js

import axiosInstance from '../../../api/axiosconfig';

// Backend'deki AppRelationshipViewSet'in ana yolu
const API_ENDPOINT = 'nexuscore/app-relationships/';

/**
 * Kullanıcının görmeye yetkili olduğu tüm uygulama ilişkilerini listeler.
 * (Backend, bunu sadece kullanıcının sahip olduğu/erişebildiği app'ler için filtreler)
 */
export const getAppRelationships = async () => {
  try {
    const response = await axiosInstance.get(API_ENDPOINT);
    return response.data;
  } catch (error) {
    console.error("Uygulama ilişkileri alınırken hata oluştu:", error);
    throw error;
  }
};

/**
 * Yeni bir uygulama ilişkisi (JOIN) oluşturur.
 * @param {object} relData - { app: (id), left_table: (id), left_column: "col_a", right_table: (id), right_column: "col_b", join_type: "LEFT JOIN" }
 */
export const createAppRelationship = async (relData) => {
  try {
    const response = await axiosInstance.post(API_ENDPOINT, relData);
    return response.data;
  } catch (error) {
    console.error("Yeni uygulama ilişkisi oluşturulurken hata:", error);
    throw error;
  }
};

/**
 * Mevcut bir uygulama ilişkisini günceller.
 */
export const updateAppRelationship = async (id, relData) => {
  try {
    const response = await axiosInstance.patch(`${API_ENDPOINT}${id}/`, relData);
    return response.data;
  } catch (error) {
    console.error(`ID'si ${id} olan ilişki güncellenirken hata:`, error);
    throw error;
  }
};

/**
 * Bir uygulama ilişkisini siler.
 */
export const deleteAppRelationship = async (id) => {
  try {
    await axiosInstance.delete(`${API_ENDPOINT}${id}/`);
  } catch (error) {
    console.error(`ID'si ${id} olan ilişki silinirken hata:`, error);
    throw error;
  }
};