// frontend/src/components/formforgeapi/components/reusable/Modal.jsx
import React from 'react';
import styles from '../../css/Modal.module.css';

/**
 * Proje genelinde kullanılacak temel Modal bileşeni.
 * @param {boolean} isOpen - Modalın açık olup olmadığını belirler.
 * @param {function} onClose - Modal kapatıldığında çağrılacak fonksiyon.
 * @param {string} title - Modal başlığı.
 * @param {React.ReactNode} children - Modalın gövdesinde gösterilecek içerik.
 */
const Modal = ({ isOpen, onClose, title, children }) => {
    if (!isOpen) {
        return null;
    }

    // Modal açıkken arkadaki içeriğin kaymasını engellemek için
    React.useEffect(() => {
        document.body.style.overflow = 'hidden';
        return () => {
            document.body.style.overflow = 'unset';
        };
    }, []);

    return (
        <div className={styles.modalBackdrop} onClick={onClose}>
            <div className={styles.modalContent} onClick={(e) => e.stopPropagation()}>
                <div className={styles.modalHeader}>
                    <h2 className={styles.modalTitle}>{title}</h2>
                    <button className={styles.closeButton} onClick={onClose}>
                        &times;
                    </button>
                </div>
                <div className={styles.modalBody}>
                    {children}
                </div>
            </div>
        </div>
    );
};

export default Modal;