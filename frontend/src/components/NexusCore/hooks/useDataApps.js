// path: frontend/src/components/NexusCore/hooks/useDataApps.js

import { useState, useCallback } from 'react';
import { useApi } from './useApi';
import { useNotifications } from './useNotifications';
import * as dataAppsApi from '../api/dataAppsApi'; // Yeni API dosyamızı import ediyoruz

/**
 * DataApp (Veri Uygulamaları) ile ilgili tüm API etkileşimlerini
 * ve state yönetimini tek bir yerde toplayan özel bir hook.
 * Bu, Veri Modeli Editörü'nün ana yönetim kancasıdır.
 */
export const useDataApps = () => {
    const { addNotification } = useNotifications();

    // Veri Uygulamalarının listesi için API state'i
    const listApi = useApi(dataAppsApi.getDataApps);
    
    // CRUD işlemleri için ayrı API state'leri (yüklenme durumlarını ayırmak için)
    const createApi = useApi(dataAppsApi.createDataApp);
    const updateApi = useApi(dataAppsApi.updateDataApp);
    const deleteApi = useApi(dataAppsApi.deleteDataApp);

    // Dış dünyaya temizlenmiş veri listesini sunalım.
    // Backend'imiz DRF pagination kullandığı için ".results" bekliyoruz.
    const dataApps = listApi.data?.results || listApi.data || [];

    // Liste yenileme fonksiyonunu useCallback ile hafızada tut
    const loadDataApps = useCallback(() => {
        listApi.request();
    }, [listApi.request]); // listApi.request, useApi'den gelen stabil bir useCallback

    // CREATE işlemi için temiz arayüz
    const createApp = async (appData) => {
        const { success, data } = await createApi.request(appData);
        if (success) {
            addNotification('Veri Uygulaması başarıyla oluşturuldu.', 'success');
            loadDataApps(); // Liste anında yenilensin
        } else {
            // Hata mesajını backend'den almaya çalış
            const errorMsg = data?.error || 'Veri Uygulaması oluşturulurken bir hata oluştu.';
            addNotification(errorMsg, 'error');
        }
        return { success, data };
    };

    // UPDATE işlemi için temiz arayüz
    const updateApp = async (id, appData) => {
        const { success, data } = await updateApi.request(id, appData);
        if (success) {
            addNotification('Veri Uygulaması başarıyla güncellendi.', 'success');
            loadDataApps(); // Liste anında yenilensin
        } else {
            const errorMsg = data?.error || 'Veri Uygulaması güncellenirken bir hata oluştu.';
            addNotification(errorMsg, 'error');
        }
        return { success, data };
    };

    // DELETE işlemi için temiz arayüz
    const deleteApp = async (id) => {
        if (window.confirm('Bu Veri Uygulamasını silmek istediğinizden emin misiniz? Bu uygulamayı kullanan raporlar artık çalışmayabilir.')) {
            const { success, data } = await deleteApi.request(id);
            if (success) {
                addNotification('Veri Uygulaması başarıyla silindi.', 'success');
                loadDataApps(); // Liste anında yenilensin
            } else {
                addNotification('Uygulama silinirken bir hata oluştu.', 'error');
            }
            return { success, data };
        }
        return { success: false }; // Kullanıcı iptal etti
    };

    // Bu hook'u kullanan bileşene sunulacak public API
    return {
        dataApps,
        isLoading: listApi.loading,
        error: listApi.error,
        loadDataApps,
        createApp,
        updateApp,
        deleteApp,
        // Farklı yüklenme durumları, butonları ayrı ayrı disable edebilmek için:
        isCreating: createApi.loading,
        isUpdating: updateApi.loading,
        isDeleting: deleteApi.loading,
    };
};