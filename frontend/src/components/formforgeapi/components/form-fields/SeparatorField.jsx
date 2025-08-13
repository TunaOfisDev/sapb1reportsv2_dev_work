// path: frontend/src/components/formforgeapi/components/form-fields/SeparatorField.jsx

import React from 'react';
import styles from '../../css/form-fields.module.css';

/**
 * Yapısal Ayırıcı Alanı Bileşeni
 * --------------------------------------------------------------------
 * 'separator' tipindeki alanlar için bir <hr> (yatay çizgi) render eder.
 * Bu bileşen tamamen görseldir ve prop almaz.
 */
const SeparatorField = () => {
  return (
    <div className={styles.fieldGroup}>
      <hr className={styles.structuralSeparator} />
    </div>
  );
};

export default SeparatorField;