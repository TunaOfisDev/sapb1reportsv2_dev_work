// frontend/src/components/ProductConfig/hooks/usePCConfiguration.js
import { useState, useCallback, useEffect } from 'react';
import pcConfigurationService from '../../../api/pcConfigurationService';
import usePCApi from './usePCApi';
import pcLogger from '../utils/pcLogger'; // pcLogger import edildi

const usePCConfiguration = () => {
    const [currentQuestion, setCurrentQuestion] = useState(null);
    const [options, setOptions] = useState([]);
    const [variantId, setVariantId] = useState(null);
    const [variantInfo, setVariantInfo] = useState(null);
    const [visibleQuestions, setVisibleQuestions] = useState([]); // Görünür soruları tut
    const [dependentRules, setDependentRules] = useState([]); // Bağımlı kuralları tut
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const [isCompleted, setIsCompleted] = useState(false);
    const [questionHistory, setQuestionHistory] = useState([]);
    const { deleteVariant } = usePCApi();
    const [oldComponentCodes, setOldComponentCodes] = useState([]);

    // Yeni eklenen state: answers
    const [answers, setAnswers] = useState({});

    const resetConfigurationState = useCallback(() => {
        setCurrentQuestion(null);
        setOptions([]);
        setVariantId(null);
        setVariantInfo(null);
        setQuestionHistory([]);
        setAnswers({}); // Yanıtları temizle
        localStorage.removeItem('variant_id'); // LocalStorage'dan da temizle
    }, []);

    const fetchInitialQuestion = useCallback(async () => {
        try {
            setLoading(true);
            setError(null);
            const response = await pcConfigurationService.getInitialQuestion();
            pcLogger.log('Initial Question Response:', response);
            
            if (response.next_question) {
                setCurrentQuestion(response.next_question);
                setOptions(response.next_question.options || []);
                setQuestionHistory([response.next_question.id]); // İlk soruyu geçmişe ekle
                // Eğer varsa görünür soruları ayarla
                setVisibleQuestions(response.visible_questions || []);
                setDependentRules(response.dependent_rules || []);
            }
            setLoading(false);
        } catch (err) {
            setError('Başlangıç sorusu yüklenirken bir hata oluştu');
            pcLogger.error('Başlangıç sorusu yüklenirken bir hata oluştu:', err);
            setLoading(false);
        }
    }, []);

    const handleAnswer = useCallback(async (answer, questionId) => {
        if (!currentQuestion) return;

        try {
            setLoading(true);
            setError(null);

            const response = await pcConfigurationService.saveAnswer({
                variant_id: variantId,
                question_id: currentQuestion.id,
                answer,
                question_type: currentQuestion.question_type
            });

            // Yanıtı answers state'ine ekle
            setAnswers(prevAnswers => ({
                ...prevAnswers,
                [questionId]: answer,
            }));

            if (response.variant_id) {
                setVariantId(response.variant_id);
            }

            if (response.variant_info) {
                setVariantInfo(response.variant_info);
                // Eski bileşen kodlarını set et
                if (response.variant_info.old_component_codes) {
                    setOldComponentCodes(response.variant_info.old_component_codes);
                }
            }

            if (response.dependent_rules) {
                setDependentRules(response.dependent_rules);
            }

            if (response.visible_questions) {
                setVisibleQuestions(response.visible_questions);
            }

            // Konfigürasyon tamamlanma durumunu kontrol et
            if (response.is_complete) {
                setIsCompleted(true);
                setCurrentQuestion(null);
                setOptions([]);
                pcLogger.info('Konfigürasyon tamamlandı.');
            } else if (response.next_question) {
                setCurrentQuestion(response.next_question);
                setOptions(response.next_question.options || []);
                setQuestionHistory(prevHistory => [...prevHistory, response.next_question.id]);
                pcLogger.info('Yeni soru yüklendi.');
            }

            setLoading(false);
        } catch (err) {
            setError('Cevap kaydedilirken bir hata oluştu');
            pcLogger.error('Cevap kaydedilirken bir hata oluştu:', err);
            setLoading(false);
        }
    }, [currentQuestion, variantId]);

    const handleBack = useCallback(async () => {
        try {
            setLoading(true);
            setError(null);

            // Soru geçmişini kontrol et
            if (questionHistory.length === 0) {
                pcLogger.warn('İlk sorudasınız, geri dönemezsiniz.');
                setLoading(false);
                return;
            }

            // İlk soruya dönülüyorsa tüm state'i temizle
            if (questionHistory.length === 1) {
                resetConfigurationState();
                await fetchInitialQuestion();
                pcLogger.info('İlk soruya dönüldü, state temizlendi.');
                setLoading(false);
                return;
            }

            if (!variantId) {
                pcLogger.warn('Variant ID bulunamadı.');
                setLoading(false);
                return;
            }

            const response = await pcConfigurationService.revertToPreviousQuestion(variantId);
            pcLogger.log('Revert Response:', response);

            if (response.question) {
                // Son soruyu geçmişten çıkar
                const updatedHistory = questionHistory.slice(0, -1);
                setQuestionHistory(updatedHistory);

                // Yanıtı answers state'inden kaldır
                setAnswers(prevAnswers => {
                    const updatedAnswers = { ...prevAnswers };
                    delete updatedAnswers[response.question.id];
                    return updatedAnswers;
                });

                // Yeni soruyu ve seçeneklerini ayarla
                setCurrentQuestion(response.question);
                setOptions(response.question.options || []);

                if (response.variant_info) {
                    setVariantInfo(response.variant_info);
                }
            }

            setLoading(false);
        } catch (err) {
            if (err.response?.status === 400) {
                // Eğer ilk soruya dönülüyorsa tüm state'i temizle
                resetConfigurationState();
                await fetchInitialQuestion();
                pcLogger.warn('İlk soruya dönüldü, state temizlendi.');
            } else {
                setError('Önceki soruya dönülürken bir hata oluştu');
                pcLogger.error('Önceki soruya dönülürken bir hata oluştu:', err);
            }
            setLoading(false);
        }
    }, [variantId, questionHistory, fetchInitialQuestion, resetConfigurationState]);

    useEffect(() => {
        fetchInitialQuestion();
    }, [fetchInitialQuestion]);

    // resetConfiguration fonksiyonunu güncelliyoruz
    const resetConfiguration = useCallback(async () => {
        try {
            if (variantId) {
                // Önce varyantı siliyoruz
                await deleteVariant(variantId);
                pcLogger.info(`Varyant silindi: ${variantId}`);
            }
            // Sonra state'i temizliyoruz
            resetConfigurationState();
            pcLogger.info('Konfigürasyon state i temizlendi.');
            // Ve yeni soruyu yüklüyoruz
            await fetchInitialQuestion();
            pcLogger.info('Yeni başlangıç sorusu yüklendi.');
        } catch (err) {
            setError('Varyant silinirken bir hata oluştu');
            pcLogger.error('Varyant silinirken bir hata oluştu:', err);
        }
    }, [variantId, deleteVariant, resetConfigurationState, fetchInitialQuestion]);

    // İlk soruya gelip gelmediğimizi kontrol eden fonksiyon
    const isFirstQuestion = useCallback(() => {
        return questionHistory.length === 0;
    }, [questionHistory]);

    // Soru görünürlüğünü kontrol eden yardımcı fonksiyon
    const isQuestionVisible = useCallback((questionId) => {
        return visibleQuestions.includes(questionId);
    }, [visibleQuestions]);

    // Soru için bağımlı kuralları getiren yardımcı fonksiyon
    const getQuestionDependentRules = useCallback((questionId) => {
        return dependentRules.filter(rule => rule.parent_question_id === questionId);
    }, [dependentRules]);

    return {
        currentQuestion,
        options,
        variantId,
        variantInfo,
        loading,
        error,
        isCompleted,
        oldComponentCodes,
        handleAnswer,
        handleBack,
        resetConfiguration,
        isFirstQuestion,
        isQuestionVisible,
        getQuestionDependentRules,
        dependentRules,
        visibleQuestions,
        answers, // Yanıtları dışarıya aktarıyoruz
    };
};

export default usePCConfiguration;