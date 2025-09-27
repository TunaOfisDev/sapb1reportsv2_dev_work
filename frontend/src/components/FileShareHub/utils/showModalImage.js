// frontend/src/components/FileShareHub/utils/showModalImage.js
import React, { useEffect } from 'react';
import '../css/showmodalimage.css';

const ShowModalImage = ({ showModal, imageUrl, closeModal }) => {
  useEffect(() => {
    // Klavye olaylarını dinle
    const handleKeyDown = (event) => {
      if (event.key === 'Escape' || event.key === ' ') {
        closeModal();
      }
    };

    // Klavye olay dinleyicisini ekle
    window.addEventListener('keydown', handleKeyDown);

    // Olay dinleyicisini temizle
    return () => {
      window.removeEventListener('keydown', handleKeyDown);
    };
  }, [closeModal]);

  // Modalın dışında tıklanıldığında kapat
  const handleModalClick = (event) => {
    if (event.target === event.currentTarget) {
      closeModal();
    }
  };

  if (!showModal) {
    return null;
  }

  return (
    <div 
      className="modal-image-container" 
      tabIndex="-1" 
      onClick={handleModalClick}
    >
      <div className="modal-image-close" onClick={closeModal}>&times;</div>
      <img src={imageUrl} alt="Product" className="modal-image-content" />
    </div>
  );
};

export default ShowModalImage;
