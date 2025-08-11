// path: frontend/src/components/formforgeapi/components/canvas/FormCanvas.jsx

import React from 'react';
import { useDroppable } from '@dnd-kit/core';
import { SortableContext, rectSortingStrategy } from '@dnd-kit/sortable';
import styles from '../../css/FormCanvas.module.css';
import FormFieldCard from '../cards/FormFieldCard';

const FormCanvas = ({ layout, selectedFieldId, onSelectField }) => {
  const { setNodeRef } = useDroppable({ id: 'canvas-drop-area' });

  // Şimdilik basitlik adına tek bir satır ve bölüm varsayıyoruz.
  const mainRow = layout[0]?.rows[0];

  if (!mainRow) {
    return (
      <div ref={setNodeRef} className={`${styles.canvas} ${styles.canvasEmpty}`}>
        <p>Başlamak için sol panelden bir alan sürükleyin.</p>
      </div>
    );
  }

  // Sıralanabilir elemanların ID listesi
  const fieldIds = mainRow.fields.map(f => f.id);

  return (
    <div ref={setNodeRef} className={styles.canvas}>
      <SortableContext items={fieldIds} strategy={rectSortingStrategy}>
        <div className={styles.canvasGrid}>
          {mainRow.fields.map(field => (
            <FormFieldCard
              key={field.id}
              field={field}
              isSelected={selectedFieldId === field.id}
              onSelect={onSelectField}
            />
          ))}
        </div>
      </SortableContext>
    </div>
  );
};

export default FormCanvas;