// frontend\src\components\ProductConfig\pages\PCVariantPage.js
import React, { useState, useEffect, useCallback } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useSelector, useDispatch } from 'react-redux';
import { fetchVariantDetails, selectCurrentVariant, selectVariantLoading, selectVariantError } from '../store/pcVariantSlice';
import PCLayout from '../layout/PCLayout';
import PCButton from '../common/PCButton';
import PCModal from '../common/PCModal';
import { formatPrice, formatDate } from '../utils/pcHelpers';
import '../css/PCVariantPage.css';

const PCVariantPage = () => {
    const { variantId } = useParams();  // URL'den variantId'yi alıyoruz
    const navigate = useNavigate();  // Sayfalar arası yönlendirme için
    const dispatch = useDispatch();  // Redux aksiyonlarını dispatch etmek için
    const variantDetails = useSelector(selectCurrentVariant);  // Varyant detayları
    const loading = useSelector(selectVariantLoading);  // Yüklenme durumu
    const error = useSelector(selectVariantError);  // Hata durumu
    const [isDeleteModalOpen, setIsDeleteModalOpen] = useState(false);  // Silme onayı modal durumu

    // Varyant bilgilerini almak için useEffect kullanıyoruz
    useEffect(() => {
        if (variantId) {
            dispatch(fetchVariantDetails(variantId));  // Varyant detaylarını getiriyoruz
        }
    }, [dispatch, variantId]);

    // Varyant düzenleme fonksiyonu
    const handleEditConfiguration = useCallback(() => {
        if (variantId) {
            navigate(`/configurator/${variantId}`);  // Düzenleme sayfasına yönlendirme
        }
    }, [navigate, variantId]);

    // Yeni varyant oluşturma fonksiyonu
    const handleCreateNewConfiguration = useCallback(() => {
        navigate('/configurator');  // Yeni konfigürasyon sayfasına yönlendirme
    }, [navigate]);

    // Varyant silme işlemi için modal açma fonksiyonu
    const handleDeleteVariant = useCallback(() => {
        setIsDeleteModalOpen(true);  // Modal'ı açıyoruz
    }, []);

    // Varyantı silme onayı işlemi
    const confirmDelete = useCallback(async () => {
        try {
            // Silme işlemi buraya gelecek
            // await dispatch(deleteVariant(variantId));
            setIsDeleteModalOpen(false);  // Modal'ı kapatıyoruz
            navigate('/configurator/variants');  // Varyantlar listesine geri dönüyoruz
        } catch (err) {
            console.error('Error deleting variant:', err);
        }
    }, [navigate]);

    // Yüklenme durumu
    if (loading) return <div className="pc-variant-page__loading">Yükleniyor...</div>;
    
    // Hata durumu
    if (error) return <div className="pc-variant-page__error">Hata: {error}</div>;

    // Varyant detayları gelmezse null döndür
    if (!variantDetails) return null;

    return (
        <PCLayout>
            <div className="pc-variant-page">
                <h1 className="pc-variant-page__title">Varyant Detayları</h1>
                <div className="pc-variant-page__details">
                    <p><strong>Proje Adı:</strong> {variantDetails.project_name}</p>
                    <p><strong>Varyant Kodu:</strong> {variantDetails.variant_code}</p>
                    <p><strong>Açıklama:</strong> {variantDetails.variant_description}</p>
                    <p><strong>Toplam Fiyat:</strong> {formatPrice(variantDetails.total_price)}</p>
                    <p><strong>Oluşturulma Tarihi:</strong> {formatDate(variantDetails.created_at)}</p>
                    <p><strong>Son Güncelleme:</strong> {formatDate(variantDetails.updated_at)}</p>
                </div>
                <h2 className="pc-variant-page__subtitle">Seçilen Özellikler</h2>
                <ul className="pc-variant-page__options-list">
                    {variantDetails.selected_options.map((option, index) => (
                        <li key={index} className="pc-variant-page__option-item">
                            <span className="pc-variant-page__option-question">{option.question}: </span>
                            <strong className="pc-variant-page__option-answer">{option.answer}</strong>
                            {option.price_modifier && (
                                <span className="pc-variant-page__option-price">
                                    ({formatPrice(option.price_modifier)})
                                </span>
                            )}
                        </li>
                    ))}
                </ul>
                <div className="pc-variant-page__actions">
                    <PCButton onClick={handleEditConfiguration} variant="primary">
                        Konfigürasyonu Düzenle
                    </PCButton>
                    <PCButton onClick={handleCreateNewConfiguration} variant="secondary">
                        Yeni Konfigürasyon Oluştur
                    </PCButton>
                    <PCButton onClick={handleDeleteVariant} variant="danger">
                        Varyantı Sil
                    </PCButton>
                </div>
            </div>

            <PCModal
                isOpen={isDeleteModalOpen}
                onClose={() => setIsDeleteModalOpen(false)}
                title="Varyantı Sil"
            >
                <p>Bu varyantı silmek istediğinizden emin misiniz?</p>
                <div className="pc-variant-page__modal-actions">
                    <PCButton onClick={confirmDelete} variant="danger">Evet, Sil</PCButton>
                    <PCButton onClick={() => setIsDeleteModalOpen(false)} variant="secondary">İptal</PCButton>
                </div>
            </PCModal>
        </PCLayout>
    );
};

export default PCVariantPage;

