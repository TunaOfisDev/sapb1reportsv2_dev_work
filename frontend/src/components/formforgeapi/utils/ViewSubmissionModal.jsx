// path: frontend/src/components/formforgeapi/utils/ViewSubmissionModal.jsx

import React, { useEffect } from 'react';
import ReactDOM from 'react-dom';
import styles from '../css/ViewSubmissionModal.module.css'; // Sizin BEM CSS dosyanız

// Bu bileşen, reactstrap'e HİÇBİR bağımlılığı olmayan, sıfırdan bir modal oluşturur.
const ViewSubmissionModal = ({ isOpen, onClose, submission }) => {
  // 'Escape' tuşuna basıldığında modal'ı kapatmak için
  useEffect(() => {
    const handleKeyDown = (event) => {
      if (event.keyCode === 27) {
        onClose();
      }
    };
    if (isOpen) {
      window.addEventListener('keydown', handleKeyDown);
    }
    return () => {
      window.removeEventListener('keydown', handleKeyDown);
    };
  }, [isOpen, onClose]);

  // Eğer modal açık değilse veya veri yoksa, render etme.
  if (!isOpen || !submission) {
    return null;
  }

  // ReactDOM.createPortal kullanarak modal'ı <body>'nin sonuna render ediyoruz.
  // Bu, onu tüm kapsayıcı div'lerin CSS etkisinden kurtarır.
  return ReactDOM.createPortal(
    // Overlay (arka plan)
    <div className={styles.viewModal__overlay} onClick={onClose}>
      {/* Modal içeriği - Tıklamanın overlay'e geçmesini engeller */}
      <div className={styles.viewModal} onClick={(e) => e.stopPropagation()}>
        
        <div className={styles.viewModal__header}>
          <h5 className={styles.viewModal__title}>
            Form Gönderim Detayı (ID: {submission.id})
          </h5>
          <button type="button" className={styles.viewModal__closeButton} aria-label="Close" onClick={onClose}>&times;</button>
        </div>

        <div className={styles.viewModal__body}>
          <div className={styles.viewModal__dataGrid}>
            {submission.values?.length > 0 ? (
              submission.values.map(item => (
                <React.Fragment key={item.form_field}>
                  <dt className={styles.viewModal__dataLabel}>{item.form_field_label || 'Alan'}</dt>
                  <dd className={styles.viewModal__dataValue}>{item.value || "—"}</dd>
                </React.Fragment>
              ))
            ) : (
              <p>Bu gönderim için gösterilecek alan verisi bulunamadı.</p>
            )}
          </div>
          <hr className={styles.viewModal__divider} />
          <div className={styles.viewModal__dataGrid}>
            <dt className={styles.viewModal__dataLabel}>Gönderen</dt>
            <dd className={styles.viewModal__dataValue}>{submission.created_by?.email}</dd>
            <dt className={styles.viewModal__dataLabel}>Tarih</dt>
            <dd className={styles.viewModal__dataValue}>{new Date(submission.created_at).toLocaleString()}</dd>
          </div>
        </div>

        <div className={styles.viewModal__footer}>
          <button type="button" className="btn btn-secondary" onClick={onClose}>
            Kapat
          </button>
        </div>
      </div>
    </div>,
    document.body // Portal'ın hedefi: document.body
  );
};

export default ViewSubmissionModal;