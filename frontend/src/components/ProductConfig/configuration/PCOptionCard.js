// frontend/src/components/ProductConfig/configuration/PCOptionCard.js
import React, { useState } from 'react';
import { useSelector } from 'react-redux';
import { selectCurrency } from '../store/pcSettingsSlice';
import PropTypes from 'prop-types';
import { formatPrice } from '../utils/pcHelpers';
import '../css/PCOptionCard.css';

import pcLogger from '../utils/pcLogger';

const PCOptionCard = ({ 
    option, 
    isSelected, 
    onSelect, 
    disabled = false,
    highlightPopular = false,
    showDescription = false,
    activePrice // Aktif fiyat prop'u eklendi
}) => {
    const [imageError, setImageError] = useState(false);
    const currencyConfig = useSelector(selectCurrency);

    // Option kontrolü bileşenin içinde yapılır
    if (!option) {
        pcLogger.warn('Option prop is missing or invalid');
        return null;
    }

    const handleClick = () => {
        if (!disabled && onSelect) {
            onSelect(option.id);
        }
    };

    const handleImageError = () => {
        setImageError(true);
    };

    const cardClasses = `
        pc-option-card 
        ${isSelected ? 'pc-option-card--selected' : ''}
        ${disabled ? 'pc-option-card--disabled' : ''}
        ${highlightPopular && option.is_popular ? 'pc-option-card--popular' : ''}
    `.trim();

    return (
        <div 
            className={cardClasses}
            onClick={handleClick}
            role="button"
            tabIndex={0}
            aria-pressed={isSelected}
            aria-disabled={disabled}
            onKeyPress={(e) => {
                if (e.key === 'Enter' || e.key === ' ') {
                    handleClick();
                }
            }}
        >
            <div className="pc-option-card__image-container">
                {option.image_url && !imageError ? (
                    <img 
                        src={option.image_url} 
                        alt={option.name} 
                        className="pc-option-card__image"
                        onError={handleImageError}
                        loading="lazy"
                    />
                ) : (
                    <div className="pc-option-card__image-placeholder">
                        <div className="pc-option-card__no-image-icon">
                            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                                <rect x="3" y="3" width="18" height="18" rx="2" ry="2"/>
                                <circle cx="8.5" cy="8.5" r="1.5"/>
                                <path d="M21 15l-5-5L5 21"/>
                            </svg>
                            <span className="pc-option-card__no-image-text">Resim Yok</span>
                        </div>
                    </div>
                )}
                {option.is_popular && highlightPopular && (
                    <span className="pc-option-card__popular-badge">Popüler</span>
                )}
            </div>

            <div className="pc-option-card__content">
                <h3 className="pc-option-card__title">{option.name}</h3>
                {option.item_code && (
                    <p className="pc-option-card__code">Kod: {option.item_code}</p>
                )}
                {activePrice !== undefined && activePrice !== 0 && (
                    <p className="pc-option-card__price">
                        {formatPrice(activePrice, currencyConfig)}
                    </p>
                )}
                {option.color_status && (
                    <p className="pc-option-card__color-status">
                        Renk Durumu: {option.color_status === 'both' ? 'Renkli/Renksiz' : option.color_status}
                    </p>
                )}
                {showDescription && option.description && (
                    <p className="pc-option-card__description">{option.description}</p>
                )}
            </div>

            {disabled && (
                <div className="pc-option-card__disabled-overlay">
                    <span>Seçilemez</span>
                </div>
            )}
        </div>
    );
};

PCOptionCard.propTypes = {
    option: PropTypes.shape({
        id: PropTypes.number.isRequired,
        name: PropTypes.string.isRequired,
        item_code: PropTypes.string,
        normal_price: PropTypes.oneOfType([PropTypes.number, PropTypes.string]),
        price_melamine: PropTypes.oneOfType([PropTypes.number, PropTypes.string]),
        price_laminate: PropTypes.oneOfType([PropTypes.number, PropTypes.string]),
        price_veneer: PropTypes.oneOfType([PropTypes.number, PropTypes.string]),
        price_lacquer: PropTypes.oneOfType([PropTypes.number, PropTypes.string]),
        melamine_triggers: PropTypes.arrayOf(PropTypes.number),
        laminate_triggers: PropTypes.arrayOf(PropTypes.number),
        veneer_triggers: PropTypes.arrayOf(PropTypes.number),
        lacquer_triggers: PropTypes.arrayOf(PropTypes.number),
        color_status: PropTypes.string,
        image_url: PropTypes.string,
        is_popular: PropTypes.bool,
        description: PropTypes.string,
        applicable_brands: PropTypes.array,
        applicable_groups: PropTypes.array,
        applicable_categories: PropTypes.array,
        applicable_product_models: PropTypes.array
    }).isRequired,
    isSelected: PropTypes.bool.isRequired,
    onSelect: PropTypes.func.isRequired,
    disabled: PropTypes.bool,
    highlightPopular: PropTypes.bool,
    showDescription: PropTypes.bool,
    activePrice: PropTypes.oneOfType([PropTypes.number, PropTypes.string])
};

export default PCOptionCard;
