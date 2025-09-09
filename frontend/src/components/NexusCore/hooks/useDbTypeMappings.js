// path: frontend/src/components/NexusCore/hooks/useDbTypeMappings.js

import { useCallback } from 'react';
import { useApi } from './useApi';
import { useNotifications } from './useNotifications';
import * as dbTypeMappingsApi from '../api/dbTypeMappingsApi';

/**
 * DBTypeMapping (Veri Tipi Eşleştirmeleri) ile ilgili tüm API etkileşimlerini
 * ve state yönetimini tek bir yerde toplayan özel bir hook.
 * Bu hook, özellikle yönetici paneli arayüzü için tasarlanmıştır.
 */
export const useDbTypeMappings = () => {
    const { addNotification } = useNotifications();

    // Veri tipi eşleştirme listesi için API state'i
    const listApi = useApi(dbTypeMappingsApi.getDBTypeMappings);
    
    // CRUD işlemleri için ayrı API state'leri
    const updateApi = useApi(dbTypeMappingsApi.updateDBTypeMapping);
    const deleteApi = useApi(dbTypeMappingsApi.deleteDBTypeMapping);

    // Dış dünyaya temizlenmiş veri listesini sunalım.
    const mappings = listApi.data?.results || listApi.data || [];

    // Liste yenileme fonksiyonunu useCallback ile hafızada tut
    const loadMappings = useCallback(() => {
        listApi.request();
    }, [listApi.request]);

    // UPDATE işlemi için temiz arayüz
    const updateMapping = async (id, mappingData) => {
        const { success, error } = await updateApi.request(id, mappingData);
        if (success) {
            addNotification('Veri tipi eşleştirmesi başarıyla güncellendi.', 'success');
            loadMappings(); // Liste anında yenilensin
        } else {
            const errorMsg = error?.message || 'Veri tipi eşleştirmesi güncellenirken bir hata oluştu.';
            addNotification(errorMsg, 'error');
        }
        return { success, error };
    };

    // DELETE işlemi için temiz arayüz
    const deleteMapping = async (id) => {
        if (window.confirm('Bu veri tipi eşleştirmesini silmek istediğinizden emin misiniz?')) {
            const { success, error } = await deleteApi.request(id);
            if (success) {
                addNotification('Veri tipi eşleştirmesi başarıyla silindi.', 'success');
                loadMappings(); // Liste anında yenilensin
            } else {
                const errorMsg = error?.message || 'Veri tipi eşleştirmesi silinirken bir hata oluştu.';
                addNotification(errorMsg, 'error');
            }
            return { success, error };
        }
        return { success: false }; // Kullanıcı iptal etti
    };

    // Bu hook'u kullanan bileşene sunulacak public API
    return {
        mappings,
        isLoading: listApi.loading,
        error: listApi.error,
        loadMappings,
        updateMapping,
        deleteMapping,
        isUpdating: updateApi.loading,
        isDeleting: deleteApi.loading,
    };
};