// path: frontend/src/components/NexusCore/api/reportTemplatesApi.js

import axiosInstance from '../../../api/axiosconfig';

// Backend'deki ReportTemplateViewSet'in ana yolu
const API_ENDPOINT = 'nexuscore/report-templates';

/**
 * Kullanıcının görmeye yetkili olduğu tüm rapor şablonlarını listeler.
 */
export const getReportTemplates = async () => {
  try {
    const response = await axiosInstance.get(`${API_ENDPOINT}/`);
    return response.data;
  } catch (error) {
    console.error("Rapor şablonları alınırken hata oluştu:", error);
    throw error;
  }
};

/**
 * Belirli bir ID'ye sahip rapor şablonunun detaylarını getirir.
 */
export const getReportTemplateById = async (id) => {
  try {
    const response = await axiosInstance.get(`${API_ENDPOINT}/${id}/`);
    return response.data;
  } catch (error) {
    console.error(`ID'si ${id} olan rapor şablonu alınırken hata:`, error);
    throw error;
  }
};

/**
 * Yeni bir rapor şablonu oluşturur.
 * @param {object} templateData - { title, description, source_virtual_table_id, configuration_json, sharing_status }
 */
export const createReportTemplate = async (templateData) => {
  try {
    const response = await axiosInstance.post(`${API_ENDPOINT}/`, templateData);
    return response.data;
  } catch (error) {
    console.error("Yeni rapor şablonu oluşturulurken hata:", error);
    throw error;
  }
};

/**
 * Mevcut bir rapor şablonunu günceller.
 */
export const updateReportTemplate = async (id, templateData) => {
  try {
    const response = await axiosInstance.patch(`${API_ENDPOINT}/${id}/`, templateData);
    return response.data;
  } catch (error) {
    console.error(`ID'si ${id} olan rapor şablonu güncellenirken hata:`, error);
    throw error;
  }
};

/**
 * Bir rapor şablonunu siler.
 */
export const deleteReportTemplate = async (id) => {
  try {
    await axiosInstance.delete(`${API_ENDPOINT}/${id}/`);
  } catch (error) {
    console.error(`ID'si ${id} olan rapor şablonu silinirken hata:`, error);
    throw error;
  }
};

/**
 * Bir rapor şablonunu çalıştırır. Backend, kaynak sorguyu çalıştırıp
 * şablonu veriye uygulayarak nihai sonucu döndürür.
 * @param {number} id - Çalıştırılacak şablonun ID'si.
 */
export const executeReportTemplate = async (id) => {
    try {
        const response = await axiosInstance.post(`${API_ENDPOINT}/${id}/execute/`);
        return response.data;
    } catch (error) {
        console.error(`ID'si ${id} olan rapor şablonu çalıştırılırken hata:`, error);
        throw error;
    }
};