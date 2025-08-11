// path: frontend/src/components/formforgeapi/components/cards/FormFieldCard.js

import React from 'react';
import { useSortable } from '@dnd-kit/sortable';
import { CSS } from '@dnd-kit/utilities';
import styles from '../../css/FormFieldCard.module.css';

const FormFieldCard = ({ field, isSelected, onSelect }) => {
  const {
    attributes,
    listeners,
    setNodeRef,
    transform,
    transition,
    isDragging,
  } = useSortable({ id: field.id });

  const style = {
    transform: CSS.Transform.toString(transform),
    transition,
  };

  const handleClick = (e) => {
    e.stopPropagation();
    onSelect(field.id);
  };

  // Dinamik olarak CSS sınıflarını birleştirmek için bir dizi kullanıyoruz.
  const cardClasses = [
    styles.formFieldCard, // Ana sınıf
    isSelected ? styles['formFieldCard--selected'] : '',
    isDragging ? styles['formFieldCard--dragging'] : '',
  ].join(' ');

  return (
    <div
      ref={setNodeRef}
      style={style}
      className={cardClasses}
      onClick={handleClick}
    >
      {/* Sürükleme tutamacı (listeners sadece bu elemana eklendi) */}
      <div {...attributes} {...listeners} className={styles.formFieldCard__dragHandle}>
        ⠿
      </div>
      
      {/* Kartın ana içeriği */}
      <div className={styles.formFieldCard__mainContent}>
        <div className={styles.formFieldCard__header}>
          <span className={styles.formFieldCard__label}>{field.label || "Etiketsiz Alan"}</span>
        </div>
        
        <div className={styles.formFieldCard__badges}>
          <span className={styles.formFieldCard__badge}>{field.field_type}</span>
          {field.is_required && (
            <span className={`${styles.formFieldCard__badge} ${styles['formFieldCard__badge--required']}`}>
              Zorunlu
            </span>
          )}
        </div>
      </div>
    </div>
  );
};

export default FormFieldCard;