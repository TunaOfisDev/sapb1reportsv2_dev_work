// path: frontend/src/components/NexusCore/hooks/useAppRelationships.js

import { useState, useCallback } from 'react';
import { useApi } from './useApi';
import { useNotifications } from './useNotifications';
import * as appRelationshipsApi from '../api/appRelationshipsApi'; // Yeni API dosyamızı import ediyoruz

/**
 * AppRelationship (JOIN İlişkileri) ile ilgili tüm API etkileşimlerini yöneten hook.
 * NOT: Backend, sadece kullanıcının sahip olduğu App'lere ait ilişkileri döndürür.
 */
export const useAppRelationships = (notifyListOwner = null) => {
    const { addNotification } = useNotifications();

    const listApi = useApi(appRelationshipsApi.getAppRelationships);
    const createApi = useApi(appRelationshipsApi.createAppRelationship);
    const updateApi = useApi(appRelationshipsApi.updateAppRelationship);
    const deleteApi = useApi(appRelationshipsApi.deleteAppRelationship);

    // Tüm ilişkileri (pagination'sız varsayıyoruz, veya results kullanıyoruz)
    const relationships = listApi.data?.results || listApi.data || [];

    const loadRelationships = useCallback(() => {
        listApi.request();
    }, [listApi.request]);
    
    /**
     * DataApp detay sayfası gibi bir yerden çağrılırsa, liste yenilemesi için 
     * o sayfayı (parent) bilgilendirecek bir callback.
     * Bu, DataApp'in 'relationships' dizisini taze tutar.
     */
    const notifyParent = () => {
        if (typeof notifyListOwner === 'function') {
            notifyListOwner();
        }
    };

    // CREATE
    const createRelationship = async (relData) => {
        const { success, data } = await createApi.request(relData);
        if (success) {
            addNotification('JOIN ilişkisi başarıyla eklendi.', 'success');
            loadRelationships(); // Bu hook'un kendi listesini yenile
            notifyParent();     // Parent'ın (DataApp detayı) listesini de yenilemesini tetikle
        } else {
            // Serializer'dan gelen detaylı hatayı göster
            const errorDetail = data?.detail || Object.values(data).flat().join(' ');
            addNotification(`İlişki oluşturulamadı: ${errorDetail || 'Bilinmeyen hata.'}`, 'error');
        }
        return { success, data };
    };

    // UPDATE
    const updateRelationship = async (id, relData) => {
        const { success, data } = await updateApi.request(id, relData);
        if (success) {
            addNotification('JOIN ilişkisi güncellendi.', 'success');
            loadRelationships();
            notifyParent();
        } else {
            const errorDetail = data?.detail || Object.values(data).flat().join(' ');
            addNotification(`İlişki güncellenemedi: ${errorDetail || 'Bilinmeyen hata.'}`, 'error');
        }
        return { success, data };
    };

    // DELETE
    const deleteRelationship = async (id) => {
        if (window.confirm('Bu JOIN ilişkisini silmek istediğinizden emin misiniz?')) {
            const { success } = await deleteApi.request(id);
            if (success) {
                addNotification('İlişki başarıyla silindi.', 'success');
                loadRelationships();
                notifyParent();
            } else {
                addNotification('İlişki silinirken bir hata oluştu.', 'error');
            }
            return { success };
        }
        return { success: false };
    };

    return {
        relationships,
        isLoading: listApi.loading,
        error: listApi.error,
        loadRelationships,
        createRelationship,
        updateRelationship,
        deleteRelationship,
        isCreating: createApi.loading,
        isUpdating: updateApi.loading,
        isDeleting: deleteApi.loading,
    };
};