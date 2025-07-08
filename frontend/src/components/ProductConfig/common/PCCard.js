// frontend/src/components/ProductConfig/common/PCCard.js
import React from 'react';
import PropTypes from 'prop-types';
import '../css/PCCard.css';

const PCCard = ({ 
    children, 
    title, 
    subtitle,
    image,
    onClick,
    selected = false,
    disabled = false,
    className = '',
    variant = 'default',
    elevation = 1,
    header,
    footer,
    actions,
    hoverEffect = false,
    rounded = false,
    bordered = false,
    fullWidth = false,
    ...props
}) => {
    const cardClasses = `
        pc-card
        pc-card--${variant}
        pc-card--elevation-${elevation}
        ${selected ? 'pc-card--selected' : ''}
        ${disabled ? 'pc-card--disabled' : ''}
        ${hoverEffect ? 'pc-card--hover-effect' : ''}
        ${rounded ? 'pc-card--rounded' : ''}
        ${bordered ? 'pc-card--bordered' : ''}
        ${fullWidth ? 'pc-card--full-width' : ''}
        ${className}
    `.trim();

    const handleClick = (e) => {
        if (!disabled && onClick) {
            onClick(e);
        }
    };

    return (
        <div 
            className={cardClasses}
            onClick={handleClick}
            {...props}
        >
            {header && <div className="pc-card__header">{header}</div>}
            {image && (
                <div className="pc-card__image-container">
                    <img src={image} alt={title} className="pc-card__image" />
                </div>
            )}
            <div className="pc-card__content">
                {title && <h3 className="pc-card__title">{title}</h3>}
                {subtitle && <p className="pc-card__subtitle">{subtitle}</p>}
                {children}
            </div>
            {actions && <div className="pc-card__actions">{actions}</div>}
            {footer && <div className="pc-card__footer">{footer}</div>}
        </div>
    );
};

PCCard.propTypes = {
    children: PropTypes.node,
    title: PropTypes.string,
    subtitle: PropTypes.string,
    image: PropTypes.string,
    onClick: PropTypes.func,
    selected: PropTypes.bool,
    disabled: PropTypes.bool,
    className: PropTypes.string,
    variant: PropTypes.oneOf(['default', 'outlined', 'filled']),
    elevation: PropTypes.oneOf([0, 1, 2, 3]),
    header: PropTypes.node,
    footer: PropTypes.node,
    actions: PropTypes.node,
    hoverEffect: PropTypes.bool,
    rounded: PropTypes.bool,
    bordered: PropTypes.bool,
    fullWidth: PropTypes.bool
};

export default PCCard;