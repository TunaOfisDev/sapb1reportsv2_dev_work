// path: frontend/src/components/formforgeapi/utils/ViewSubmissionModal.jsx

import React, { useEffect } from 'react';
import ReactDOM from 'react-dom';
import styles from '../css/ViewSubmissionModal.module.css';

const ViewSubmissionModal = ({ isOpen, onClose, submission }) => {
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

  if (!isOpen || !submission) {
    return null;
  }

  return ReactDOM.createPortal(
    <div className={styles.viewModal__overlay} onClick={onClose}>
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
                  <dd className={styles.viewModal__dataValue}>
                    {Array.isArray(item.value) ? item.value.join(', ') : (item.value || "—")}
                  </dd>
                </React.Fragment>
              ))
            ) : (
              <p>Bu gönderim için gösterilecek alan verisi bulunamadı.</p>
            )}
          </div>
          <hr className={styles.viewModal__divider} />
          <div className={styles.viewModal__dataGrid}>
            <dt className={styles.viewModal__dataLabel}>Versiyon</dt>
            <dd className={styles.viewModal__dataValue}>V{submission.version}</dd>
            {submission.parent_submission && (
                 <React.Fragment>
                    <dt className={styles.viewModal__dataLabel}>Ana Gönderim ID</dt>
                    <dd className={styles.viewModal__dataValue}>{submission.parent_submission}</dd>
                 </React.Fragment>
            )}
            <dt className={styles.viewModal__dataLabel}>Gönderen</dt>
            <dd className={styles.viewModal__dataValue}>{submission.created_by?.email}</dd>
            <dt className={styles.viewModal__dataLabel}>Tarih</dt>
            <dd className={styles.viewModal__dataValue}>{new Date(submission.created_at).toLocaleString()}</dd>
          </div>
        </div>

        <div className={styles.viewModal__footer}>
          <button 
            type="button" 
            className={`${styles.button} ${styles.button_secondary}`} 
            onClick={onClose}
          >
            Kapat
          </button>
        </div>
      </div>
    </div>,
    document.body
  );
};

export default ViewSubmissionModal;