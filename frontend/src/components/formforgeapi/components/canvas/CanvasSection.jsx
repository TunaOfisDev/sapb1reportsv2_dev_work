// path: frontend/src/components/formforgeapi/components/canvas/CanvasSection.jsx

import React from 'react';
import styles from '../../css/FormCanvas.module.css';
import CanvasRow from './CanvasRow';

const CanvasSection = ({ section, selectedFieldId, onSelectField }) => {
  return (
    <section className={styles.formCanvas__section}>
      {section?.title && (
        <h4 className={styles.formCanvas__sectionTitle}>
          {section.title}
        </h4>
      )}

      {/* GÜVENLİK GÜNCELLEMESİ: 'section.rows' varsa map'le */}
      {/* section?.rows?.map(...) ifadesi, 'section' veya 'section.rows' undefined ise çökmez. */}
      {section?.rows?.map(row => (
        // row'un da geçerli bir nesne olduğundan emin ol
        row && (
          <CanvasRow
            key={row.id}
            row={row}
            selectedFieldId={selectedFieldId}
            onSelectField={onSelectField}
          />
        )
      ))}
    </section>
  );
};

export default CanvasSection;