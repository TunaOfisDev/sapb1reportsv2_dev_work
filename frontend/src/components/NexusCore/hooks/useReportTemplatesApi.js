// path: frontend/src/components/NexusCore/hooks/useReportTemplatesApi.js

import { useState, useEffect, useCallback } from 'react';
import { useApi } from './useApi';
import { useNotifications } from './useNotifications';
import * as reportTemplatesApi from '../api/reportTemplatesApi';

/**
 * Rapor Şablonları (Report Templates) ile ilgili tüm API etkileşimlerini
 * ve state yönetimini tek bir yerde toplayan özel bir hook.
 */
export const useReportTemplates = () => {
    const { addNotification } = useNotifications();

    // API hook'larını bu çatı altında merkezi olarak yönetiyoruz.
    const { data: templatesResponse, loading: isLoading, error, request: fetchTemplates } = useApi(reportTemplatesApi.getReportTemplates);
    const createApi = useApi(reportTemplatesApi.createReportTemplate);
    const updateApi = useApi(reportTemplatesApi.updateReportTemplate);
    const deleteApi = useApi(reportTemplatesApi.deleteReportTemplate);

    // Dış dünyaya sadece temizlenmiş veriyi (results dizisini) sunalım.
    const templates = templatesResponse?.results || [];

    // Bileşenin ilk yüklendiğinde verileri çekmek için.
    // useCallback ile fonksiyonun kimliğinin sabit kalmasını sağlıyoruz.
    const loadTemplates = useCallback(() => {
        fetchTemplates();
    }, [fetchTemplates]);

    // CREATE işlemi için temiz bir arayüz
    const createTemplate = async (templateData) => {
        const { success, data } = await createApi.request(templateData);
        if (success) {
            addNotification('Rapor başarıyla oluşturuldu.', 'success');
            fetchTemplates(); // Listeyi anında yenile
        } else {
            addNotification('Rapor oluşturulurken bir hata oluştu.', 'error');
        }
        return { success, data };
    };

    // UPDATE işlemi için temiz bir arayüz
    const updateTemplate = async (id, templateData) => {
        const { success, data } = await updateApi.request(id, templateData);
        if (success) {
            addNotification('Rapor başarıyla güncellendi.', 'success');
            fetchTemplates(); // Listeyi anında yenile
        } else {
            addNotification('Rapor güncellenirken bir hata oluştu.', 'error');
        }
        return { success, data };
    };

    // DELETE işlemi için temiz bir arayüz
    const deleteTemplate = async (id) => {
        if (window.confirm('Bu raporu silmek istediğinizden emin misiniz?')) {
            const { success, data } = await deleteApi.request(id);
            if (success) {
                addNotification('Rapor başarıyla silindi.', 'success');
                fetchTemplates(); // Listeyi anında yenile
            } else {
                addNotification('Rapor silinirken bir hata oluştu.', 'error');
            }
            return { success, data };
        }
        return { success: false }; // Kullanıcı iptal etti
    };

    // Bu hook'u kullanan bileşenlere sunacağımız arayüz (public API)
    return {
        templates,
        isLoading,
        error,
        loadTemplates,
        createTemplate,
        updateTemplate,
        deleteTemplate,
        // Yüklenme durumlarını daha detaylı vermek için
        isCreating: createApi.loading,
        isUpdating: updateApi.loading,
        isDeleting: deleteApi.loading,
    };
};