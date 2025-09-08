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
 * * ### MİMARİ GÜNCELLEME ###
 * Artık 'source_virtual_table_id' DEĞİL, 'source_data_app_id' gönderiyoruz.
 * @param {object} templateData - { title, description, source_data_app_id, configuration_json, sharing_status }
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
 * ### STRATEJİK DEVİR: BU FONKSİYONUN ANLAMI DEĞİŞTİ ###
 * * Bir rapor şablonunu "ÇALIŞTIRIR". 
 * * ESKİ STRATEJİ: Backend'den HAM VERİ ve konfigürasyon çekerdi. Frontend pivot yapardı.
 * YENİ STRATEJİ: Backend'deki "DAHİ" pivot motorunu tetikler. Backend, DataApp'i okur,
 * tüm JOIN'leri ve GROUP BY'ları veritabanında çalıştırır ve frontend'e SADECE
 * NİHAİ, HAZIR PİVOT VERİSİNİ döndürür.
 * * @param {number} id - Çalıştırılacak şablonun ID'si.
 * @returns {Promise<Object>} Başarılıysa: { success: true, columns: [...], rows: [...] } formatında PİVOTLANMIŞ veri.
 * Başarısızsa: Hata fırlatır (axios interceptor halleder) veya { success: false, error: "..." } döner.
 */
export const executeReportTemplate = async (id) => {
    try {
        const response = await axiosInstance.post(`${API_ENDPOINT}/${id}/execute/`);
        return response.data; // Bu veri artık PİŞMİŞ veridir.
    } catch (error) {
        console.error(`ID'si ${id} olan rapor şablonu çalıştırılırken hata:`, error);
        // Hata yönetimi (örn: 400 Bad Request) axios interceptor'ınızda
        // veya bu fonksiyonu çağıran yerde yapılmalı.
        throw error;
    }
};