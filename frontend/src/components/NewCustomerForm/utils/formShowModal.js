// frontend/src/components/NewCustomerForm/utils/formShowModal.js
import React, { useEffect } from 'react';
import '../css/FormShowModal.css';
import NewCustomerForm from '../forms/NewCustomerForm';

const FormShowModal = ({ isOpen, onClose, formData, onSubmit }) => {
  // ESC tuşu ile kapatma
  useEffect(() => {
    const handleEsc = (e) => {
      if (e.keyCode === 27 && isOpen) onClose();
    };
    window.addEventListener('keydown', handleEsc);
    return () => window.removeEventListener('keydown', handleEsc);
  }, [onClose, isOpen]);

  // Erken return'u useEffect'ten sonra yapıyoruz
  if (!isOpen) return null;

  const handleSubmit = async (data) => {
    try {
      await onSubmit(data);
      onClose();
    } catch (error) {
      console.error('Form gönderirken hata:', error);
    }
  };

  // Overlay'e tıklandığında modalı kapat
  const handleOverlayClick = (e) => {
    if (e.target.className === 'modal-overlay') {
      onClose();
    }
  };

  return (
    <div className="modal-overlay" onClick={handleOverlayClick}>
      <div className="modal-container">
        <div className="modal-header">
          <h2>Müşteri Formu Düzenle</h2>
          <div className="modal-controls">
            <button 
              onClick={onClose} 
              className="modal-close-button"
              title="Kapat (ESC)"
            >
              <span className="modal-close-icon">×</span>
              <span className="modal-close-text">Kapat</span>
            </button>
          </div>
        </div>
        <div className="modal-content">
          <NewCustomerForm 
            initialData={formData}
            onSubmit={handleSubmit}
            isEdit={true}
          />
        </div>
      </div>
    </div>
  );
};

export default FormShowModal;