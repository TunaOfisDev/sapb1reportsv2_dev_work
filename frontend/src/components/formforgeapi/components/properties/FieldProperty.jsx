// path: frontend/src/components/formforgeapi/components/properties/FieldProperty.jsx
import React from 'react';
import styles from '../../css/FieldPropsDrawer.module.css';

/**
 * FieldProperty Bileşeni
 * --------------------------------------------------------------------
 * FieldPropsDrawer içerisinde tek bir özellik satırını (etiket + form elemanı)
 * render etmek için kullanılan, yeniden kullanılabilir bir "aptal" bileşendir.
 *
 * Sorumlulukları:
 * - Bir etiket (label) ve bir form elemanını (`children`) props olarak alır.
 * - Bu iki elemanı, tutarlı bir stil ve yapı içinde sarmallar.
 * - Hiçbir iş mantığı veya state barındırmaz. Sadece aldığı props'ları render eder.
 *
 * @param {string} label - Form elemanının solunda/üstünde görünecek etiket metni.
 * @param {string} [htmlFor] - Label'ın `for` attribute'u. Erişilebilirlik için,
 * içerideki form elemanının ID'si ile eşleşmelidir.
 * @param {React.ReactNode} children - Render edilecek asıl form elemanı (input, select, checkbox vb.).
 */
const FieldProperty = ({ label, htmlFor, children }) => {
  return (
    <div className={styles.fieldPropsDrawer__group}>
      {label && (
        <label htmlFor={htmlFor} className={styles.fieldPropsDrawer__label}>
          {label}
        </label>
      )}
      {children}
    </div>
  );
};

export default FieldProperty;