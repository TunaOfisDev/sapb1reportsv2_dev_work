// frontend/src/components/ProductConfig/utils/pcVariantLengthCalculation.js
import React from 'react';
import '../css/pcVariantLengthCalculation.css';

const VariantLengthCalculator = ({ code, description }) => {
    // Sabitleri tanımla
    const CODE_MAX_LENGTH = 50;
    const DESCRIPTION_MAX_LENGTH = 200;

    // Uzunlukları hesapla
    const codeLength = code?.length || 0;
    const descriptionLength = description?.length || 0;

    // Limit durumlarını kontrol et
    const isCodeExceeded = codeLength > CODE_MAX_LENGTH;
    const isDescriptionExceeded = descriptionLength > DESCRIPTION_MAX_LENGTH;

    // Kalan karakter sayılarını hesapla
    const remainingCodeChars = CODE_MAX_LENGTH - codeLength;
    const remainingDescriptionChars = DESCRIPTION_MAX_LENGTH - descriptionLength;

    return (
        <div className="variant-length-calculator">
            <div className="length-info-container">
                <div className="length-info">
                    <span className="length-label">Varyant Kodu:</span>
                    <span className={`length-count ${isCodeExceeded ? 'exceeded' : 'valid'}`}>
                        {codeLength} / {CODE_MAX_LENGTH}
                        <span className="remaining-chars">
                            ({remainingCodeChars >= 0 ? `${remainingCodeChars} karakter kaldı` : `${Math.abs(remainingCodeChars)} karakter fazla`})
                        </span>
                    </span>
                </div>
                
                <div className="length-info">
                    <span className="length-label">Varyant Açıklaması:</span>
                    <span className={`length-count ${isDescriptionExceeded ? 'exceeded' : 'valid'}`}>
                        {descriptionLength} / {DESCRIPTION_MAX_LENGTH}
                        <span className="remaining-chars">
                            ({remainingDescriptionChars >= 0 ? `${remainingDescriptionChars} karakter kaldı` : `${Math.abs(remainingDescriptionChars)} karakter fazla`})
                        </span>
                    </span>
                </div>
            </div>

            {/* Uyarı mesajlarını göster */}
            <div className="warnings">
                {isCodeExceeded && (
                    <div className="warning-message">
                        Varyant kodu {CODE_MAX_LENGTH} karakteri aşmamalıdır!
                    </div>
                )}
                {isDescriptionExceeded && (
                    <div className="warning-message">
                        Varyant açıklaması {DESCRIPTION_MAX_LENGTH} karakteri aşmamalıdır!
                    </div>
                )}
            </div>
        </div>
    );
};

export default VariantLengthCalculator;