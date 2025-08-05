// path: frontend/src/components/formforgeapi/components/canvas/FormCanvas.jsx

import React from 'react';
import styles from '../../css/FormCanvas.module.css';
import CanvasSection from './CanvasSection';

const FormCanvas = ({ layout, selectedFieldId, onSelectField }) => {
  // DEĞİŞİKLİK: isCanvasEmpty ? ... : ... mantığını kaldırıyoruz.
  // Layout boş bile olsa, içindeki section ve row'ların render edilmesine izin veriyoruz
  // ki "bırakma alanı" her zaman DOM'da mevcut olsun.

  // Eğer layout henüz yüklenmediyse (boş dizi ise) hiçbir şey gösterme.
  if (!layout || layout.length === 0) {
    // Veya bir yükleniyor durumu gösterilebilir. Şimdilik boş bırakalım.
    return <main className={styles.formCanvas}></main>;
  }

  return (
    <main className={styles.formCanvas}>
      {layout.map(section => (
        <CanvasSection
          key={section.id}
          section={section}
          selectedFieldId={selectedFieldId}
          onSelectField={onSelectField}
        />
      ))}
    </main>
  );
};

export default FormCanvas;