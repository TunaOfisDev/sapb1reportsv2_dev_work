// frontend/src/components/productpicture/utils/PictureModal.js
import React, { useEffect } from 'react';
import '../css/ProductPictureTable.css';

const PictureModal = ({ showModal, imageUrl, closeModal }) => {
  useEffect(() => {
    // Klavye olaylarını dinle
    const handleKeyDown = (event) => {
      if (event.key === 'Escape' || event.key === ' ') {
        closeModal();
      }
    };

    // Klavye olay dinleyicisini ekleyin
    window.addEventListener('keydown', handleKeyDown);

    // Olay dinleyicisini temizleyin
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
      className="product-picture-table__image-modal" 
      tabIndex="-1" 
      onClick={handleModalClick} // Modalın dışında tıklama olayını dinle
    >
      <div className="product-picture-table__close" onClick={closeModal}>&times;</div>
      <img src={imageUrl} alt="Product" />
    </div>
  );
};

export default PictureModal;
