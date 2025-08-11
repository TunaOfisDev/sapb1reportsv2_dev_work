// path: frontend/src/components/formforgeapi/components/form-fields/HeadingField.jsx

import React from 'react';
import styles from '../../css/form-fields.module.css';

/**
 * Yapısal Başlık Alanı Bileşeni
 * --------------------------------------------------------------------
 * 'heading' tipindeki alanlar için bir <h2> başlık elementi render eder.
 * Bu bileşen kullanıcıdan veri almaz, sadece görsel bir elemandır.
 *
 * @param {object} field - Render edilecek alanın şema bilgisi ('label' kullanılır).
 */
const HeadingField = ({ field }) => {
  return (
    <div className={styles.fieldGroup}>
      <h2 className={styles.structuralHeading}>{field.label}</h2>
    </div>
  );
};

export default HeadingField;