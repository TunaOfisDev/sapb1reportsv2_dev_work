// frontend/src/components/ProductConfig/common/PCModal.js
import React, { useEffect, useCallback } from 'react';
import PropTypes from 'prop-types';
import '../css/PCModal.css';

const PCModal = ({
    isOpen,
    onClose,
    title,
    children,
    size = 'medium',
    className = '',
    showCloseButton = true,
    closeOnOverlayClick = true,
    closeOnEscape = true,
    animation = 'fade',
    footer,
    fullScreen = false,
    centered = false,
    scrollable = false,
    backdropOpacity = 0.5,
    zIndex = 1000,
    onAfterOpen,
    onAfterClose
}) => {
    const handleClose = useCallback(() => {
        onClose();
        if (onAfterClose) {
            onAfterClose();
        }
    }, [onClose, onAfterClose]);

    const handleKeyDown = useCallback((event) => {
        if (event.key === 'Escape' && closeOnEscape) {
            handleClose();
        }
    }, [closeOnEscape, handleClose]);

    useEffect(() => {
        if (isOpen) {
            document.addEventListener('keydown', handleKeyDown);
            document.body.style.overflow = 'hidden';
            if (onAfterOpen) {
                onAfterOpen();
            }
        }

        return () => {
            document.removeEventListener('keydown', handleKeyDown);
            document.body.style.overflow = 'visible';
        };
    }, [isOpen, handleKeyDown, onAfterOpen]);

    if (!isOpen) return null;

    const modalClasses = `
        pc-modal
        pc-modal--${size}
        pc-modal--${animation}
        ${fullScreen ? 'pc-modal--fullscreen' : ''}
        ${centered ? 'pc-modal--centered' : ''}
        ${scrollable ? 'pc-modal--scrollable' : ''}
        ${className}
    `.trim();

    return (
        <div 
            className="pc-modal-overlay" 
            onClick={closeOnOverlayClick ? handleClose : undefined}
            style={{ backgroundColor: `rgba(0, 0, 0, ${backdropOpacity})`, zIndex }}
        >
            <div 
                className={modalClasses} 
                onClick={(e) => e.stopPropagation()}
                role="dialog"
                aria-modal="true"
                aria-labelledby="modal-title"
            >
                <div className="pc-modal__header">
                    <h2 id="modal-title" className="pc-modal__title">{title}</h2>
                    {showCloseButton && (
                        <button className="pc-modal__close" onClick={handleClose} aria-label="Close">
                            &times;
                        </button>
                    )}
                </div>
                <div className="pc-modal__content">
                    {children}
                </div>
                {footer && (
                    <div className="pc-modal__footer">
                        {footer}
                    </div>
                )}
            </div>
        </div>
    );
};

PCModal.propTypes = {
    isOpen: PropTypes.bool.isRequired,
    onClose: PropTypes.func.isRequired,
    title: PropTypes.string,
    children: PropTypes.node,
    size: PropTypes.oneOf(['small', 'medium', 'large']),
    className: PropTypes.string,
    showCloseButton: PropTypes.bool,
    closeOnOverlayClick: PropTypes.bool,
    closeOnEscape: PropTypes.bool,
    animation: PropTypes.oneOf(['fade', 'slide-up', 'slide-down', 'zoom']),
    footer: PropTypes.node,
    fullScreen: PropTypes.bool,
    centered: PropTypes.bool,
    scrollable: PropTypes.bool,
    backdropOpacity: PropTypes.number,
    zIndex: PropTypes.number,
    onAfterOpen: PropTypes.func,
    onAfterClose: PropTypes.func
};

export default PCModal;