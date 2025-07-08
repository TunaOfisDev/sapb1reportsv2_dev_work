// frontend/src/components/ProductConfig/hooks/useHanaData.js
import { useState, useCallback } from 'react';
import pcHanaService from '../../../api/pcHanaService';

const useHanaData = (variantId) => {
    // State tanımlamaları
    const [hanaData, setHanaData] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    // HANA verilerini güncelleme fonksiyonu
    const updateHanaData = useCallback(async () => {
        if (!variantId) return;

        try {
            setLoading(true);
            setError(null);

            // HANA verilerini güncelle
            const updateResult = await pcHanaService.updateHanaData(variantId);
            
            if (!updateResult.success) {
                throw new Error(updateResult.error);
            }

            // Güncel HANA detaylarını al
            const detailsResult = await pcHanaService.getVariantHanaDetails(variantId);
            
            if (!detailsResult.success) {
                throw new Error(detailsResult.error);
            }

            setHanaData(detailsResult.data);
            console.log('HANA verileri güncellendi:', detailsResult.data);

        } catch (err) {
            setError(err.message || 'HANA verileri güncellenirken bir hata oluştu');
            console.error('HANA veri güncelleme hatası:', err);
        } finally {
            setLoading(false);
        }
    }, [variantId]);

    // HANA detaylarını alma fonksiyonu
    const fetchHanaDetails = useCallback(async () => {
        if (!variantId) return;

        try {
            setLoading(true);
            setError(null);

            const result = await pcHanaService.getVariantHanaDetails(variantId);
            
            if (!result.success) {
                throw new Error(result.error);
            }

            setHanaData(result.data);
            console.log('HANA detayları alındı:', result.data);

        } catch (err) {
            setError(err.message || 'HANA detayları alınırken bir hata oluştu');
            console.error('HANA detayları alma hatası:', err);
        } finally {
            setLoading(false);
        }
    }, [variantId]);

    // Hata temizleme fonksiyonu
    const clearError = useCallback(() => {
        setError(null);
    }, []);

    // HANA verilerini temizleme fonksiyonu
    const clearHanaData = useCallback(() => {
        setHanaData(null);
    }, []);

    return {
        hanaData,          // HANA verileri
        loading,           // Yükleme durumu
        error,            // Hata durumu
        updateHanaData,    // HANA verilerini güncelleme fonksiyonu
        fetchHanaDetails,  // HANA detaylarını alma fonksiyonu
        clearError,        // Hata temizleme fonksiyonu
        clearHanaData,     // HANA verilerini temizleme fonksiyonu
        isHanaDataAvailable: !!hanaData // HANA verilerinin mevcut olup olmadığı
    };
};

export default useHanaData;