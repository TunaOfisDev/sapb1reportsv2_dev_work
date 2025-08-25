// path: frontend/src/components/NexusCore/components/common/Modal/Modal.jsx
import React, { useEffect } from 'react';
import ReactDOM from 'react-dom';
import PropTypes from 'prop-types';
import { X } from 'react-feather';
import styles from './Modal.module.scss';

/**
 * Proje genelinde kullanılacak, erişilebilirlik özellikleri eklenmiş Modal bileşeni.
 * React Portal kullanarak, DOM'da body'nin sonuna eklenir.
 */
const Modal = ({ title, isOpen, onClose, children, footer, className = '' }) => {
  // Escape tuşuna basıldığında modal'ı kapatmak için bir useEffect hook'u.
  useEffect(() => {
    const handleKeyDown = (event) => {
      if (event.key === 'Escape') {
        onClose();
      }
    };

    if (isOpen) {
      document.addEventListener('keydown', handleKeyDown);
      // Modal açıldığında body'nin kaymasını engelle
      document.body.style.overflow = 'hidden';
    }

    // Cleanup fonksiyonu: Bileşen kaldırıldığında event listener'ı temizle.
    return () => {
      document.removeEventListener('keydown', handleKeyDown);
      document.body.style.overflow = 'auto';
    };
  }, [isOpen, onClose]);

  if (!isOpen) {
    return null;
  }

  const modalClasses = `${styles.modal} ${className}`.trim();

  // ReactDOM.createPortal kullanarak modal'ı document.body'nin içine render ediyoruz.
  return ReactDOM.createPortal(
    <div 
      className={styles.overlay} 
      onClick={onClose} 
      role="dialog" 
      aria-modal="true" 
      aria-labelledby="modal-title"
    >
      <div className={modalClasses} onClick={(e) => e.stopPropagation()}>
        <header className={styles.modal__header}>
          <h3 id="modal-title" className={styles.modal__title}>{title}</h3>
          <button className={styles.closeButton} onClick={onClose} aria-label="Kapat">
            <X size={24} />
          </button>
        </header>
        <main className={styles.modal__body}>
          {children}
        </main>
        {footer && (
          <footer className={styles.modal__footer}>
            {footer}
          </footer>
        )}
      </div>
    </div>,
    document.body // Portal'ın hedefi
  );
};

Modal.propTypes = {
  title: PropTypes.string.isRequired,
  isOpen: PropTypes.bool.isRequired,
  onClose: PropTypes.func.isRequired,
  children: PropTypes.node.isRequired,
  footer: PropTypes.node,
  className: PropTypes.string,
};

export default Modal;