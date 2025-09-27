// frontend/src/components/ProductConfig/common/PCButton.js
import React from 'react';
import PropTypes from 'prop-types';
import '../css/PCButton.css';

const PCButton = ({ 
    onClick, 
    children, 
    type = 'button', 
    variant = 'primary', 
    size = 'medium', 
    disabled = false,
    fullWidth = false,
    className = '',
    icon,
    iconPosition = 'left',
    loading = false,
    loadingText = 'Loading...',
    rounded = false,
    outlined = false,
    elevated = false,
    animated = false,
    ...props
}) => {
    const buttonClasses = `
        pc-button 
        pc-button--${variant} 
        pc-button--${size}
        ${fullWidth ? 'pc-button--full-width' : ''}
        ${rounded ? 'pc-button--rounded' : ''}
        ${outlined ? 'pc-button--outlined' : ''}
        ${elevated ? 'pc-button--elevated' : ''}
        ${animated ? 'pc-button--animated' : ''}
        ${loading ? 'pc-button--loading' : ''}
        ${className}
    `.trim();

    const renderIcon = () => {
        if (!icon) return null;
        return <span className={`pc-button__icon pc-button__icon--${iconPosition}`}>{icon}</span>;
    };

    const renderContent = () => {
        if (loading) {
            return (
                <>
                    <span className="pc-button__spinner"></span>
                    {loadingText}
                </>
            );
        }
        return (
            <>
                {iconPosition === 'left' && renderIcon()}
                <span className="pc-button__text">{children}</span>
                {iconPosition === 'right' && renderIcon()}
            </>
        );
    };

    return (
        <button
            type={type}
            className={buttonClasses}
            onClick={onClick}
            disabled={disabled || loading}
            {...props}
        >
            {renderContent()}
        </button>
    );
};

PCButton.propTypes = {
    onClick: PropTypes.func,
    children: PropTypes.node.isRequired,
    type: PropTypes.oneOf(['button', 'submit', 'reset']),
    variant: PropTypes.oneOf(['primary', 'secondary', 'outline', 'text', 'success', 'warning', 'danger']),
    size: PropTypes.oneOf(['small', 'medium', 'large']),
    disabled: PropTypes.bool,
    fullWidth: PropTypes.bool,
    className: PropTypes.string,
    icon: PropTypes.node,
    iconPosition: PropTypes.oneOf(['left', 'right']),
    loading: PropTypes.bool,
    loadingText: PropTypes.string,
    rounded: PropTypes.bool,
    outlined: PropTypes.bool,
    elevated: PropTypes.bool,
    animated: PropTypes.bool
};

export default PCButton;