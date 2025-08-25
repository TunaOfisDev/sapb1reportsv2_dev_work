/* path: frontend/src/components/NexusCore/api/virtualTablesApi.js */

/* Projenizin ana Axios yapılandırmasını import ediyoruz. */
import axiosInstance from '../../../api/axiosconfig';

/* Bu modülün konuşacağı ana endpoint'i tanımlıyoruz. */
const API_ENDPOINT = 'nexuscore/virtual-tables/';

/**
 * Kullanıcının görmeye yetkili olduğu tüm sanal tabloları listeler.
 * (Backend, kullanıcının kendi özel tablolarını ve halka açık tabloları döndürür.)
 * @returns {Promise<Array>} Sanal tablo listesini içeren bir promise döndürür.
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
 * @param {number} id Sanal tablo ID'si.
 * @returns {Promise<Object>} Sanal tablo detaylarını içeren bir promise döndürür.
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
 * @param {object} tableData - { title, sql_query, connection_id, sharing_status } formatında veri.
 * @returns {Promise<Object>} Oluşturulan yeni sanal tablo nesnesini döndürür.
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
 * @param {number} id Güncellenecek sanal tablonun ID'si.
 * @param {object} tableData Güncellenecek alanları içeren nesne (örn: { title, sharing_status }).
 * @returns {Promise<Object>} Güncellenmiş sanal tablo nesnesini döndürür.
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
 * @param {number} id Silinecek sanal tablonun ID'si.
 * @returns {Promise<void>} İşlem başarılı olduğunda bir promise döndürür.
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
 * Bu, projemizin en kritik fonksiyonlarından biridir.
 * @param {number} id Çalıştırılacak sanal tablonun ID'si.
 * @returns {Promise<Object>} { success, columns, rows } formatında veri döndürür.
 */
export const executeVirtualTable = async (id) => {
    try {
        const response = await axiosInstance.post(`${API_ENDPOINT}${id}/execute/`);
        return response.data;
    } catch (error) {
        console.error(`ID'si ${id} olan sanal tablo çalıştırılırken hata:`, error);
        throw error;
    }
};