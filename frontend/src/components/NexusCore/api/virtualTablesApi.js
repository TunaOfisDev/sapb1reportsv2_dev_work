// path: frontend/src/components/NexusCore/api/virtualTablesApi.js

/* Projenizin ana Axios yapılandırmasını import ediyoruz. */
import axiosInstance from '../../../api/axiosconfig';

/* Bu modülün konuşacağı ve backend urls.py ile tam uyumlu olan ana endpoint. */
const API_ENDPOINT = 'nexuscore/virtual-tables/';

/**
 * Kullanıcının görmeye yetkili olduğu tüm sanal tabloları listeler.
 */
export const getVirtualTables = async () => {
  try {
    const response = await axiosInstance.get(API_ENDPOINT);
    return response.data;
  } catch (error) {
    console.error("Sanal tablolar alınırken hata oluştu:", error);
    throw error;
  }
};

/**
 * Belirli bir ID'ye sahip sanal tablonun detaylarını (tanımını) getirir.
 */
export const getVirtualTableById = async (id) => {
  try {
    const response = await axiosInstance.get(`${API_ENDPOINT}${id}/`);
    return response.data;
  } catch (error) {
    console.error(`ID'si ${id} olan sanal tablo alınırken hata:`, error);
    throw error;
  }
};

/**
 * Yeni bir sanal tablo oluşturur.
 */
export const createVirtualTable = async (tableData) => {
  try {
    const response = await axiosInstance.post(API_ENDPOINT, tableData);
    return response.data;
  } catch (error) {
    console.error("Yeni sanal tablo oluşturulurken hata:", error);
    throw error;
  }
};

/**
 * Mevcut bir sanal tabloyu günceller.
 */
export const updateVirtualTable = async (id, tableData) => {
  try {
    const response = await axiosInstance.patch(`${API_ENDPOINT}${id}/`, tableData);
    return response.data;
  } catch (error) {
    console.error(`ID'si ${id} olan sanal tablo güncellenirken hata:`, error);
    throw error;
  }
};

/**
 * Bir sanal tabloyu siler.
 */
export const deleteVirtualTable = async (id) => {
  try {
    await axiosInstance.delete(`${API_ENDPOINT}${id}/`);
  } catch (error) {
    console.error(`ID'si ${id} olan sanal tablo silinirken hata:`, error);
    throw error;
  }
};

/**
 * Bir sanal tablonun sorgusunu backend'de çalıştırır ve dönen veriyi alır.
 * @param {number} id - Çalıştırılacak sanal tablonun ID'si.
 * @param {object} [params={}] - (Gelecek için) Sorguya gönderilecek dinamik parametreler.
 * @returns {Promise<Object>} Sorgu sonucu (kolonlar ve satırlar).
 */
export const executeVirtualTable = async (id, params = {}) => {
    try {
        // Parametreleri POST isteğinin body'si içinde göndermek, esneklik sağlar.
        const response = await axiosInstance.post(`${API_ENDPOINT}${id}/execute/`, { params });
        return response.data;
    } catch (error) {
        console.error(`ID'si ${id} olan sanal tablo çalıştırılırken hata:`, error);
        throw error;
    }
};