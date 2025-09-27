// frontend/src/components/productpicture/utils/SkeletonLoader.js
import React from 'react';
import '../css/SkeletonLoader.css'; 

const SkeletonLoader = () => {
  return (
    <div className="skeleton-wrapper">
      <div className="skeleton-header">
        <div className="skeleton-title"></div>
        {/* Buton simülasyonları ekleniyor */}
        <div className="skeleton-button"></div>
        <div className="skeleton-button"></div>
      </div>
 
      <div className="skeleton-table">
        <div className="skeleton-row">
          <div className="skeleton-cell"></div>
        </div>
        {/* Daha fazla satır eklemek isterseniz, aşağıdaki satırları çoğaltabilirsiniz */}
        <div className="skeleton-row">
          <div className="skeleton-cell"></div>
        </div>
      </div>
    </div>
  );
};

export default SkeletonLoader;


