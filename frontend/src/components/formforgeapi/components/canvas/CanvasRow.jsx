// path: frontend/src/components/formforgeapi/components/canvas/CanvasRow.jsx

import React from 'react';
import { useDroppable } from '@dnd-kit/core';
import { SortableContext, rectSortingStrategy } from '@dnd-kit/sortable';
import styles from '../../css/FormCanvas.module.css';
import FormFieldCard from '../cards/FormFieldCard';

const CanvasRow = ({ row, selectedFieldId, onSelectField }) => {
  // GÜVENLİK GÜNCELLEMESİ: Eğer 'row' prop'u gelmezse veya 'row.fields' bir dizi değilse,
  // hata vermeden kullanılabilecek boş bir dizi ata.
  const fields = Array.isArray(row?.fields) ? row.fields : [];
  const fieldIds = fields.map(field => field.id);

  const { setNodeRef } = useDroppable({
    id: row?.id || 'default-droppable-row', // 'row' yoksa varsayılan bir id ata
  });

  return (
    <SortableContext items={fieldIds} strategy={rectSortingStrategy}>
      <div ref={setNodeRef} className={styles.formCanvas__row}>
        {fields.length === 0 ? (
          <div className={styles.formCanvas__empty}>
            <span className={styles.formCanvas__emptyIcon}>🖐️</span>
            Formunuzu oluşturmak için soldaki paletten alanları buraya sürükleyin.
          </div>
        ) : (
          fields.map((field) => (
            <FormFieldCard
              key={field.id}
              field={field}
              isSelected={field.id === selectedFieldId}
              onClick={() => onSelectField(field.id)}
            />
          ))
        )}
      </div>
    </SortableContext>
  );
};

export default CanvasRow;