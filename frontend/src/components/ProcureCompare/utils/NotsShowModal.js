// frontend/src/components/ProcureCompare/utils/NotsShowModal.js

import React, { useEffect } from 'react';
import '../css/NotsShowModal.css';

const NotsShowModal = ({ onClose }) => {
  // ESC veya boşluk ile modal kapatma
  useEffect(() => {
    const handleKeyDown = (e) => {
      if (e.key === 'Escape' || e.key === ' ') {
        onClose();
      }
    };

    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, [onClose]);

  // Modal dışında bir yere tıklanırsa kapat
  const handleBackdropClick = (e) => {
    if (e.target.classList.contains('nots-modal__backdrop')) {
      onClose();
    }
  };

  return (
    <div className="nots-modal__backdrop" onClick={handleBackdropClick}>
      <div className="nots-modal">
        <button className="nots-modal__close" onClick={onClose}>
          &times;
        </button>
        <div className="nots-modal__header">📌 Sistem Notu</div>
        <div className="nots-modal__content">
{`🛠 Yaşanan Teknik Vaka:
        
SAP Business One üzerinde yürütülen teklif karşılaştırma modülünde bir kalemde (ItemCode: 109001831830366018) farklı teklif kalem kodlarının eşleşmemesi problemi yaşandı.

📎 Tespit:
- Satır, teklif referansları ile doğru şekilde ilişkilendi.
- Ancak tekliflerde geçen kalem kodları manuel olarak değiştirilmişti veya yanlış veri girişi yapılmıştı.
- Bu nedenle sistem eşleştirme yapamadı ve TeklifFiyatlariJSON alanı boş olarak döndü.

📌 Örnek Sipariş Belge Numarası: 7347

🔍 Not:
Veri kalitesinden kaynaklı sorun olduğundan kodda değişiklik yapılmasına gerek duyulmamıştır. Yapay zeka destekli analiz bu vakayı başarıyla tanımlamıştır.

- TARZ 🤖`}
        </div>
      </div>
    </div>
  );
};

export default NotsShowModal;
