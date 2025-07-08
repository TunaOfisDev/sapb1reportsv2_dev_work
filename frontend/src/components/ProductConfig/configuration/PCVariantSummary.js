// frontend/src/components/ProductConfig/configuration/PCVariantSummary.js
import React from 'react';
import { useSelector } from 'react-redux';
import { selectCurrency } from '../store/pcSettingsSlice';
import PropTypes from 'prop-types';
import { formatPrice } from '../utils/pcHelpers';
import PCButton from '../common/PCButton';
import '../css/PCVariantSummary.css';

const PCVariantSummary = ({ 
    variantCode, 
    variantDescription, 
    totalPrice, 
    projectName,
    selectedOptions = [],
    oldComponentCodes = [],
    variantId = null, // Yeni eklenen prop
    onEdit,
    onSave,
    onPrint
}) => {
    // Redux'tan currency konfigürasyonunu al
    const currencyConfig = useSelector(selectCurrency);



    return (
        <div className="pc-variant-summary">
            <h3 className="pc-variant-summary__title">Varyant Özeti</h3>
            <div className="pc-variant-summary__content">
                {projectName && (
                    <p className="pc-variant-summary__item">
                        <span className="pc-variant-summary__label">Proje Adı:</span>
                        <span className="pc-variant-summary__value">{projectName}</span>
                    </p>
                )}
                    {variantId && (
                    <p className="pc-variant-summary__item">
                        <span className="pc-variant-summary__label">Variant ID:</span>
                        <span className="pc-variant-summary__value">{variantId}</span> 
                    </p>
                )}
                {variantCode && (
                    <p className="pc-variant-summary__item">
                        <span className="pc-variant-summary__label">Varyant Kodu:</span>
                        <span className="pc-variant-summary__value">{variantCode}</span>
                    </p>
                )}
                {variantDescription && (
                    <p className="pc-variant-summary__item">
                        <span className="pc-variant-summary__label">Açıklama:</span>
                        <span className="pc-variant-summary__value">{variantDescription}</span>
                    </p>
                )}
                {totalPrice !== undefined && (
                    <p className="pc-variant-summary__item pc-variant-summary__item--price">
                        <span className="pc-variant-summary__label">Toplam Fiyat:</span>
                        <span className="pc-variant-summary__value">
                            {formatPrice(totalPrice, currencyConfig)}
                        </span>
                    </p>
                )}
            </div>

            {selectedOptions.length > 0 && (
                <div className="pc-variant-summary__options">
                    <h4 className="pc-variant-summary__subtitle">Seçilen Özellikler</h4>
                    <ul className="pc-variant-summary__option-list">
                        {selectedOptions.map((option, index) => (
                            <li key={index} className="pc-variant-summary__option-item">
                                <span className="pc-variant-summary__option-name">{option.name}</span>
                                {option.price_modifier !== 0 && (
                                    <span className="pc-variant-summary__option-price">
                                        ({formatPrice(option.price_modifier, currencyConfig)})
                                    </span>
                                )}
                            </li>
                        ))}
                    </ul>
                </div>
            )}

            {/* Eski bileşen kodları bölümü */}
            {oldComponentCodes.length > 0 ? (
                <div className="pc-variant-summary__section">
                    <h4 className="pc-variant-summary__subtitle">Eski Bileşen Kodları</h4>
                    <div className="pc-variant-summary__code-item">
                        {/* Kodları tek satırda, virgülle ayrılmış şekilde göster */}
                        <span className="pc-variant-summary__code-text">
                            {oldComponentCodes.join(", ")}
                        </span>
                        {/* Kopyala butonu */}
                            <PCButton
                                onClick={() => {
                                    const textToCopy = oldComponentCodes.join(", ");

                                    // Clipboard API kullanımı
                                    if (navigator.clipboard && window.isSecureContext) {
                                        navigator.clipboard.writeText(textToCopy)
                                            .then(() => alert("Eski bileşen kodları kopyalandı!"))
                                            .catch((err) => console.error("Kopyalama hatası:", err));
                                    } else {
                                        // Fallback: document.execCommand
                                        const textarea = document.createElement("textarea");
                                        textarea.value = textToCopy;
                                        textarea.style.position = "fixed"; // Ekranda görünmemesi için
                                        document.body.appendChild(textarea);
                                        textarea.focus();
                                        textarea.select();
                                        try {
                                            document.execCommand("copy");
                                            alert("Eski bileşen kodları kopyalandı!");
                                        } catch (err) {
                                            console.error("Fallback kopyalama hatası:", err);
                                            alert("Kopyalama işlemi başarısız oldu!");
                                        }
                                        document.body.removeChild(textarea);
                                    }
                                }}
                                variant="text"
                                size="small"
                                className="pc-variant-summary__copy-button"
                            >
                                Kopyala
                            </PCButton>

                    </div>
                </div>
            ) : (
                <div className="pc-variant-summary__section">
                    <h4 className="pc-variant-summary__subtitle">Eski Bileşen Kodları</h4>
                    <p className="pc-variant-summary__no-codes">Eski bileşen kod yok</p>
                </div>
            )}



            <div className="pc-variant-summary__actions">
                {onEdit && (
                    <PCButton onClick={onEdit} variant="secondary">
                        Düzenle
                    </PCButton>
                )}
                {onSave && (
                    <PCButton onClick={onSave} variant="primary">
                        Kaydet
                    </PCButton>
                )}
                {onPrint && (
                    <PCButton onClick={onPrint} variant="outline">
                        Yazdır
                    </PCButton>
                )}
            </div>
        </div>
    );
};

PCVariantSummary.propTypes = {
    variantCode: PropTypes.string,
    variantDescription: PropTypes.string,
    totalPrice: PropTypes.oneOfType([
        PropTypes.number,
        PropTypes.string
    ]),
    projectName: PropTypes.string,
    selectedOptions: PropTypes.arrayOf(PropTypes.shape({
        name: PropTypes.string.isRequired,
        price_modifier: PropTypes.oneOfType([PropTypes.number, PropTypes.string])
    })),
    oldComponentCodes: PropTypes.oneOfType([
        PropTypes.arrayOf(PropTypes.string),
        PropTypes.string
    ]),
    variantId: PropTypes.oneOfType([  // Yeni eklenen prop type
        PropTypes.number,
        PropTypes.string
    ]),
    onEdit: PropTypes.func,
    onSave: PropTypes.func,
    onPrint: PropTypes.func
};

export default PCVariantSummary;