// frontend/src/components/productpicture/utils/FileNameCount.js
import React from 'react';
import '../css/FileNameCount.css';

const FileNameCount = ({ productPictures, availableImages }) => {
  // Verilerin yüklenmesini kontrol et
  if (!productPictures || !availableImages) {
    return <div>Veriler yükleniyor...</div>;
  }

  // 'availableImages' listesi içinde 'picture_name' ile eşleşen resimlerin sayısını hesapla
  const matchingFilenameCount = productPictures.filter(item => 
    availableImages.includes(item.picture_name)).length;

  // Benzersiz 'item_code' sayısı almak için Set kullan
  const uniqueItemCodeCount = new Set(productPictures.map(item => item.item_code)).size;

  return (
    <div className="filename-count-container">
      <h3 className="filename-count-container__item">Kalem Sayısı: {uniqueItemCodeCount}</h3>
      <h3 className="filename-count-container__item">Eşleşen Resim Sayısı: {matchingFilenameCount}</h3>
    </div>
  );
};

export default FileNameCount;





