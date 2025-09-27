// frontend/src/components/ProductConfig/variant/PCVariantDetails.js
import React, { useEffect, useCallback } from 'react';
import { useSelector, useDispatch } from 'react-redux';
import { useParams, useNavigate } from 'react-router-dom';
import { fetchVariantDetails, selectCurrentVariant, selectVariantLoading, selectVariantError } from '../store/pcVariantSlice';
import PCButton from '../common/PCButton';
import { formatPrice, formatDate } from '../utils/pcHelpers';
import '../css/PCVariantDetails.css';

const PCVariantDetails = () => {
    const { variantId } = useParams();
    const navigate = useNavigate();
    const dispatch = useDispatch();
    const currentVariant = useSelector(selectCurrentVariant);
    const loading = useSelector(selectVariantLoading);
    const error = useSelector(selectVariantError);

    useEffect(() => {
        if (variantId) {
            dispatch(fetchVariantDetails(variantId));
        }
    }, [dispatch, variantId]);

    const handleEditVariant = useCallback(() => {
        navigate(`/configurator/edit/${variantId}`);
    }, [navigate, variantId]);

    const handleCreateNewVariant = useCallback(() => {
        navigate('/configurator');
    }, [navigate]);

    const handlePrintVariant = useCallback(() => {
        window.print();
    }, []);

    const renderOptionsList = useCallback(() => {
        if (!currentVariant || !currentVariant.selected_options) return null;

        return (
            <ul className="pc-variant-details__options-list">
                {currentVariant.selected_options.map((option, index) => (
                    <li key={index} className="pc-variant-details__option-item">
                        <span className="pc-variant-details__option-question">{option.question}: </span>
                        <strong className="pc-variant-details__option-answer">{option.answer}</strong>
                        {option.price_modifier && (
                            <span className="pc-variant-details__option-price">
                                ({formatPrice(option.price_modifier)})
                            </span>
                        )}
                    </li>
                ))}
            </ul>
        );
    }, [currentVariant]);

    if (loading) return <div className="pc-variant-details__loading">Yükleniyor...</div>;
    if (error) return <div className="pc-variant-details__error">Hata: {error}</div>;
    if (!currentVariant) return null;

    return (
        <div className="pc-variant-details">
            <h1 className="pc-variant-details__title">Varyant Detayları</h1>
            <div className="pc-variant-details__content">
                <p><strong>Proje Adı:</strong> {currentVariant.project_name}</p>
                <p><strong>Varyant Kodu:</strong> {currentVariant.variant_code}</p>
                <p><strong>Açıklama:</strong> {currentVariant.variant_description}</p>
                <p><strong>Toplam Fiyat:</strong> {formatPrice(currentVariant.total_price)}</p>
                <p><strong>Oluşturulma Tarihi:</strong> {formatDate(currentVariant.created_at)}</p>
                <p><strong>Son Güncelleme:</strong> {formatDate(currentVariant.updated_at)}</p>
                {currentVariant.status && (
                    <p><strong>Durum:</strong> {currentVariant.status}</p>
                )}
            </div>
            <h2 className="pc-variant-details__subtitle">Seçilen Özellikler</h2>
            {renderOptionsList()}
            <div className="pc-variant-details__actions">
                <PCButton onClick={handleEditVariant} variant="primary">
                    Varyantı Düzenle
                </PCButton>
                <PCButton onClick={handleCreateNewVariant} variant="secondary">
                    Yeni Varyant Oluştur
                </PCButton>
                <PCButton onClick={handlePrintVariant} variant="outline">
                    Yazdır
                </PCButton>
            </div>
        </div>
    );
};

export default PCVariantDetails;