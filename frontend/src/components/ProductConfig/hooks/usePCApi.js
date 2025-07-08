// frontend/src/components/ProductConfig/hooks/usePCApi.js
import { useState, useCallback } from 'react';
import pcConfigurationService from '../../../api/pcConfigurationService';
import pcLogger from '../utils/pcLogger';

const usePCApi = () => {
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    const handleApiCall = useCallback(async (apiFunction, errorMessage, ...args) => {
        setLoading(true);
        setError(null);
        try {
            const response = await apiFunction(...args);
            pcLogger.log('API Response:', response);
            setLoading(false);
            return response;
        } catch (err) {
            setError(errorMessage);
            setLoading(false);
            pcLogger.error(errorMessage, err);
            throw err;
        }
    }, []);

    const getNextQuestion = useCallback(async (currentQuestionId = null, variantId = null, taxonomies = []) => {
        if (!currentQuestionId && !variantId) {
            return handleApiCall(
                pcConfigurationService.getInitialQuestion,
                'İlk soru yüklenirken bir hata oluştu.'
            );
        }
        return handleApiCall(
            pcConfigurationService.saveAnswer,
            'Soru yüklenirken bir hata oluştu.',
            { currentQuestionId, variantId, taxonomies }
        );
    }, [handleApiCall]);

    const saveAnswer = useCallback((data) => 
        handleApiCall(
            () => pcConfigurationService.saveAnswer(data),
            'Cevap kaydedilirken bir hata oluştu.'
        ),
    [handleApiCall]);

    const deleteVariant = useCallback((variantId) => 
        handleApiCall(
            () => pcConfigurationService.deleteVariant(variantId),
            'Varyant silinirken bir hata oluştu.'
        ),
    [handleApiCall]);

    const getVariantDetails = useCallback((variantId) =>
        handleApiCall(
            () => pcConfigurationService.getVariantSummary(variantId),
            'Varyant detayları alınırken bir hata oluştu.'
        ),
    [handleApiCall]);

    const getOldComponentCodes = useCallback((variantId) =>
        handleApiCall(
            () => pcConfigurationService.getVariantSummary(variantId),
            'Eski bileşen kodları alınırken bir hata oluştu.'
        ),
    [handleApiCall]);

    return {
        loading,
        error,
        getNextQuestion,
        saveAnswer,
        deleteVariant,
        getVariantDetails,
        getOldComponentCodes
    };
};

export default usePCApi;