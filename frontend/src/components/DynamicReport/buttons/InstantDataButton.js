// frontend/src/components/DynamicReport/buttons/InstantDataButton.js
import React, { useState } from 'react';
import { fetchInstantData } from '../../../api/dynamicreport';

const InstantDataButton = () => {
  const [loading, setLoading] = useState(false);
  const [dataFetched, setDataFetched] = useState(false); // Verinin daha önce alınıp alınmadığını takip etmek için bir state ekledik.

  const handleInstantDataClick = async () => {
    if (dataFetched) {
      // Veri zaten alındıysa, tekrar alma.
      return;
    }

    setLoading(true);

    try {
      // Anlık veri alma işlemini burada gerçekleştirin
      const response = await fetchInstantData();
      console.log('Anlık veri alındı:', response.data);

      // Veri alındıktan sonra isterseniz işlemler yapabilirsiniz

      setDataFetched(true); // Verinin alındığını işaretleyin.

    } catch (error) {
      console.error('Anlık veri alma hatası:', error);
    }

    setLoading(false);
  };

  return (
    <div className="instant-data-button">
      <button
        onClick={handleInstantDataClick}
        className={`btn ${loading ? 'btn-secondary' : 'btn-primary'}`}
        disabled={loading || dataFetched} // Veri alındıysa butonu devre dışı bırak
      >
        {loading ? 'Veri Alınıyor...' : 'Anlık Veri Al'}
      </button>
    </div>
  );
};

export default InstantDataButton;
