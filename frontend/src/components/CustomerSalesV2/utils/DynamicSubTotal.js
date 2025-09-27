// frontend/src/components/CustomerSalesV2/utils/DynamicSubTotal.js
import React, { useMemo, useState, useEffect } from 'react';
import PropTypes from 'prop-types';
import FormatNumber from './FormatNumber';

// 1. Yeni CSS dosyasını import et
import '../css/DynamicSubTotal.css';

const DynamicSubTotal = ({ data, columnId }) => {
  // 2. Animasyonu tetiklemek için bir state ekle
  const [isUpdating, setIsUpdating] = useState(false);

  const total = useMemo(() => {
    if (!data || data.length === 0) {
      return 0;
    }
    return data.reduce((sum, current) => {
      const value = Number(current.values?.[columnId]) || 0;
      return sum + value;
    }, 0);
  }, [data, columnId]);

  // 3. 'total' değeri her değiştiğinde bu effect çalışacak
  useEffect(() => {
    // Flaş animasyonunu başlat
    setIsUpdating(true);

    // Animasyon bittikten sonra state'i temizle ki tekrar tetiklenebilsin
    const timer = setTimeout(() => {
      setIsUpdating(false);
    }, 1000); // 1000ms = 1 saniye (animasyon süresiyle aynı)

    // Bileşen yeniden render olursa veya kaldırılırsa zamanlayıcıyı temizle
    return () => clearTimeout(timer);
  }, [total]); // Bu effect sadece 'total' değiştiğinde çalışır

  // 4. State'e göre dinamik olarak CSS sınıfını belirle
  const containerClasses = `dynamic-subtotal-container ${isUpdating ? 'updated' : ''}`;

  // 5. JSX'i stil ve animasyon için bir <span> ile sarmala
  return (
    <span className={containerClasses}>
      <FormatNumber value={total} />
    </span>
  );
};

DynamicSubTotal.propTypes = {
    data: PropTypes.array,
    columnId: PropTypes.string.isRequired,
};

export default DynamicSubTotal;