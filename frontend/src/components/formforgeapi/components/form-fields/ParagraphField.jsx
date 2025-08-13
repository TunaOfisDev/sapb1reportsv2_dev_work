// path: frontend/src/components/formforgeapi/components/form-fields/ParagraphField.jsx

import React from 'react';
import styles from '../../css/form-fields.module.css';

/**
 * Yapısal Paragraf Alanı Bileşeni
 * --------------------------------------------------------------------
 * 'paragraph' tipindeki alanlar için bir <p> paragraf elementi render eder.
 * Bu bileşen kullanıcıdan veri almaz, form içinde talimat veya açıklama
 * göstermek için kullanılır.
 *
 * @param {object} field - Render edilecek alanın şema bilgisi ('label' kullanılır).
 */
const ParagraphField = ({ field }) => {
  return (
    <div className={styles.fieldGroup}>
      <p className={styles.structuralParagraph}>{field.label}</p>
    </div>
  );
};

export default ParagraphField;