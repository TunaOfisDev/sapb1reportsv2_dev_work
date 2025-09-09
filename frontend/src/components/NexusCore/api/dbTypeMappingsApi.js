// path: frontend/src/components/NexusCore/api/dbTypeMappingsApi.js

import axiosInstance from '../../../api/axiosconfig';

// Backend'deki DBTypeMappingViewSet'in ana yolu
const API_ENDPOINT = 'nexuscore/db-type-mappings/';

/**
 * Otomatik olarak keşfedilen tüm veri tipi eşleştirmelerini listeler.
 * Bu listeyi yönetici, 'other' olarak etiketlenmiş tipleri düzeltmek için kullanır.
 */
export const getDBTypeMappings = async () => {
  try {
    const response = await axiosInstance.get(API_ENDPOINT);
    return response.data;
  } catch (error) {
    console.error("Veri tipi eşleştirmeleri alınırken hata:", error);
    throw error;
  }
};

/**
 * Mevcut bir veri tipi eşleştirmesini günceller.
 * Yöneticinin 'other' olarak etiketlenmiş bir tipi düzeltmesi için kullanılır.
 * @param {number} id - Güncellenecek eşleştirme kaydının ID'si.
 * @param {object} mappingData - { general_category: "string" | "number" | "date" | "datetime" | "other" }
 */
export const updateDBTypeMapping = async (id, mappingData) => {
  try {
    const response = await axiosInstance.patch(`${API_ENDPOINT}${id}/`, mappingData);
    return response.data;
  } catch (error) {
    console.error(`ID'si ${id} olan veri tipi eşleştirmesi güncellenirken hata:`, error);
    throw error;
  }
};

/**
 * Bir veri tipi eşleştirmesini siler.
 */
export const deleteDBTypeMapping = async (id) => {
  try {
    await axiosInstance.delete(`${API_ENDPOINT}${id}/`);
  } catch (error) {
    console.error(`ID'si ${id} olan veri tipi eşleştirmesi silinirken hata:`, error);
    throw error;
  }
};