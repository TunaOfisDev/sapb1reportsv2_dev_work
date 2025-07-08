// frontend/src/components/ProductConfig/configuration/PCConfigurationFlow.js
import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useSelector, useDispatch } from 'react-redux';
import PCQuestionCard from './PCQuestionCard';
import PCVariantSummary from './PCVariantSummary';
import PCButton from '../common/PCButton';
import PCModal from '../common/PCModal';
import VariantLengthCalculator from '../utils/pcVariantLengthCalculation';
import {
    resetConfiguration,
    selectLoading,
    selectError,
    selectIsUpdating,
    selectUpdatingMessage
} from '../store/pcConfigurationSlice';
import usePCConfiguration from '../hooks/usePCConfiguration';
import useHanaData from '../hooks/useHanaData';

const PCConfigurationFlow = () => {
    const [showDeleteModal, setShowDeleteModal] = useState(false);
    const navigate = useNavigate();
    const dispatch = useDispatch();

    // Redux selectörleri
    const loading = useSelector(selectLoading);
    const error = useSelector(selectError);
    const isUpdating = useSelector(selectIsUpdating);
    const updatingMessage = useSelector(selectUpdatingMessage);

    const {
        currentQuestion,
        options,
        variantId,
        variantInfo,
        isCompleted,
        handleAnswer,
        handleBack,
        resetConfiguration: resetConfig,
        answers, // Yanıtları saklayan yeni state
    } = usePCConfiguration(); // Güncellenmiş hook kullanımı

    const {
        hanaData,
        loading: hanaLoading,
        error: hanaError,
        updateHanaData,
        isHanaDataAvailable
    } = useHanaData(variantId);

    // HANA verilerini güncelleme efekti
    useEffect(() => {
        if (isCompleted && variantId) {
            updateHanaData();
        }
    }, [isCompleted, variantId, updateHanaData]);

    // Yeni Konfigürasyon işlemi
    const handleNewConfiguration = async () => {
        try {
            if (window.confirm('Mevcut varyantı silip yeni bir konfigürasyon başlatmak istediğinizden emin misiniz?')) {
                await resetConfig();
                dispatch(resetConfiguration());
                localStorage.removeItem('variant_id');
                navigate('/configurator', { replace: true });
                window.location.reload();
            }
        } catch (err) {
            console.error('Yeni konfigürasyon başlatma hatası:', err);
        }
    };

    // Varyant Listesi işlemine yönlendirme
    const handleGoToVariants = () => {
        navigate('/variants');
    };

    // SAP Veri Sorgulama işlemi
    const handleSapQuery = () => {
        if (variantId) {
            updateHanaData();
        }
    };

    // Yükleme veya Güncelleme Durumu
    if (loading || isUpdating) {
        return (
            <div className="pc-configuration-flow">
                <div className="pc-configuration-flow__loading">
                    <div className="pc-question-card pc-question-card--skeleton">
                        <div className="pc-question-card__header">
                            <div className="skeleton skeleton-title"></div>
                            <div className="skeleton skeleton-description"></div>
                        </div>
                        <div className="pc-question-card__content">
                            <div className="skeleton skeleton-input"></div>
                        </div>
                        <div className="pc-question-card__actions">
                            <div className="skeleton skeleton-button"></div>
                            <div className="skeleton skeleton-button"></div>
                        </div>
                    </div>
                    {isUpdating && (
                        <div className="pc-configuration-flow__updating-message">
                            {updatingMessage}
                        </div>
                    )}
                </div>
            </div>
        );
    }

    // Hata Durumu
    if (error) return <div className="pc-error">{error}</div>;

    return (
        <div className="pc-configuration-flow">
            {!isCompleted && currentQuestion && (
                <PCQuestionCard
                    question={currentQuestion}
                    options={options}
                    onAnswer={handleAnswer}
                    onBack={handleBack}
                    variantId={variantId}
                    onDeleteAndReset={resetConfig}
                    currentAnswer={answers[currentQuestion.id]} // Yanıt state'ini geçiriyoruz
                />
            )}

            <div className="pc-configuration-flow__actions">
                {isCompleted && (
                    <div className="pc-configuration-completed">
                        <h2>Konfigürasyon Tamamlandı</h2>
                        
                        {hanaLoading && (
                            <div className="pc-hana-loading">
                                <div className="skeleton skeleton-hana-title"></div>
                                <div className="skeleton skeleton-hana-detail"></div>
                                <div className="skeleton skeleton-hana-detail"></div>
                                <div className="skeleton skeleton-hana-detail"></div>
                            </div>
                        )}

                        {hanaError && (
                            <div className="pc-hana-error">
                                SAP veri hatası: {hanaError}
                            </div>
                        )}

                        {isHanaDataAvailable && (
                            <div className="pc-hana-details">
                                <h3>SAP Detayları</h3>
                                <div className="pc-hana-info">
                                    <p><strong>Ürün Kodu:</strong> {hanaData.sap_item_code}</p>
                                    <p><strong>Ürün Açıklaması:</strong> {hanaData.sap_item_description}</p>
                                    <p><strong>Eski Bileşen Kodu:</strong> {hanaData.sap_U_eski_bilesen_kod}</p>
                                    <p><strong>Fiyat:</strong> {hanaData.sap_price} {hanaData.sap_currency}</p>
                                </div>
                            </div>
                        )}
                    </div>
                )}

                {variantInfo && (
                    <PCVariantSummary
                        variantId={variantId}
                        variantCode={variantInfo.variant_code}
                        variantDescription={variantInfo.variant_description}
                        totalPrice={parseFloat(variantInfo.total_price)}
                        projectName={variantInfo.project_name}
                        oldComponentCodes={variantInfo.old_component_codes || []}
                    />
                )}

                {isCompleted && (
                    <div className="pc-configuration-completed-actions">
                        <div className="pc-button-group">
                            <PCButton
                                onClick={handleNewConfiguration}
                                variant="danger"
                                size="medium"
                            >
                                Sil ve Yeni Olustur!
                            </PCButton>

                            <PCButton
                                onClick={handleGoToVariants}
                                variant="secondary"
                                size="medium"
                            >
                                Varyant Listesi
                            </PCButton>

                            {variantId && variantInfo?.variant_code && (
                                <PCButton
                                    onClick={handleSapQuery}
                                    variant="primary"
                                    size="medium"
                                    disabled={hanaLoading}
                                >
                                    {hanaLoading ? 'Sorgulanıyor...' : 'SAP Veri Sorgula'}
                                </PCButton>
                            )}
                        </div>

                        {variantInfo && (
                            <VariantLengthCalculator
                                code={variantInfo.variant_code}
                                description={variantInfo.variant_description}
                            />
                        )}
                    </div>
                )}
            </div>

            <PCModal
    isOpen={showDeleteModal}
    onClose={() => setShowDeleteModal(false)}
    title="Sil ve Yeni Oluştur!"
>
    <p>Mevcut varyantı silip yeni bir konfigürasyon başlatmak istediğinizden emin misiniz?</p>
    <div className="pc-modal-actions">
        {/* "Sil ve Yeni Başlat" düğmesi kırmızı stilinde */}
        <PCButton 
            onClick={handleNewConfiguration} 
            variant="danger" 
            size="large"
        >
            Evet, Yeni Başlat
        </PCButton>

        {/* İptal düğmesi gri tonlarda */}
        <PCButton 
            onClick={() => setShowDeleteModal(false)} 
            variant="secondary" 
            size="medium"
        >
            İptal
        </PCButton>
    </div>
</PCModal>

        </div>
    );
};

export default PCConfigurationFlow;
