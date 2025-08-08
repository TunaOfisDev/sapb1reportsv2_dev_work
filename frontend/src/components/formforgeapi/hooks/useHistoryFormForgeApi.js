// frontend/src/components/formforgeapi/hooks/useHistoryFormForgeApi.js
import { useState, useCallback } from 'react';
import FormForgeApiApi from '../api/FormForgeApiApi';

/**
 * Gönderi versiyon geçmişini yönetmek için özelleştirilmiş hook.
 * Sorumlulukları:
 * 1. API'den geçmiş verisini çekmek.
 * 2. Modal'ın durumunu (açık/kapalı) yönetmek.
 * 3. Yüklenme (loading) ve hata durumlarını yönetmek.
 */
export const useHistoryFormForgeApi = () => {
    const [isHistoryModalOpen, setHistoryModalOpen] = useState(false);
    const [submissionHistory, setSubmissionHistory] = useState([]);
    const [selectedSubmission, setSelectedSubmission] = useState(null);
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState(null);

    const openHistoryModal = useCallback(async (submission) => {
        try {
            setIsLoading(true);
            setError(null);
            setSelectedSubmission(submission);
            const response = await FormForgeApiApi.getSubmissionHistory(submission.id);
            setSubmissionHistory(response.data);
            setHistoryModalOpen(true);
        } catch (err) {
            setError('Gönderi geçmişi yüklenirken bir hata oluştu.');
            console.error(err);
        } finally {
            setIsLoading(false);
        }
    }, []);

    const closeHistoryModal = useCallback(() => {
        setHistoryModalOpen(false);
        setSubmissionHistory([]);
        setSelectedSubmission(null);
        setError(null);
    }, []);

    return {
        isHistoryModalOpen,
        submissionHistory,
        selectedSubmission,
        isLoading,
        error,
        openHistoryModal,
        closeHistoryModal,
    };
};