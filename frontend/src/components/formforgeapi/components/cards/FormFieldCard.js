// path: frontend/src/components/formforgeapi/components/cards/FormFieldCard.js
import React from 'react';
import { useSortable } from '@dnd-kit/sortable';
import { CSS } from '@dnd-kit/utilities';
import styles from '../../css/FormFieldCard.module.css';

// İkonlar aynı kalabilir...
const fieldIcons = {
  text: 'T', number: '№', email: '@', textarea: '¶', singleselect: '▼',
  multiselect: '▼▼', checkbox: '☑', radio: '◉', date: '📅', default: '?',
};

const FormFieldCard = ({ field, isSelected, onClick }) => {
  const {
    attributes,
    listeners,
    setNodeRef,
    transform,
    transition,
    isDragging, // dnd-kit'ten gelen sürüklenme durumu
  } = useSortable({ id: field.id });

  const style = {
    transform: CSS.Transform.toString(transform),
    transition,
    opacity: isDragging ? 0.5 : 1, // Sürüklenirken hafif şeffaf yap
    zIndex: isDragging ? 100 : 'auto',
  };

  const classNames = [
    styles.formFieldCard,
    isSelected ? styles['formFieldCard--selected'] : '',
    isDragging ? styles['formFieldCard--dragging'] : '',
  ].filter(Boolean).join(' ');

  return (
    <div
      ref={setNodeRef}
      style={style}
      className={classNames}
      onClick={onClick}
      {...attributes} // Draggable attributes
    >
      <div
        {...listeners} // Drag handle'a listener'ları bağla
        className={styles.formFieldCard__dragHandle}
        title="Sıralamak için sürükle"
      >
        ⠿
      </div>

      <div className={styles.formFieldCard__header}>
        <span className={styles.formFieldCard__icon}>
          {fieldIcons[field.field_type] || fieldIcons.default}
        </span>
        <span className={styles.formFieldCard__label}>
          {field.label || "İsimsiz Alan"}
        </span>
      </div>

      <div className={styles.formFieldCard__badges}>
        <span className={styles.formFieldCard__badge}>
          {field.field_type}
        </span>
        {field.is_required && (
          <span className={`${styles.formFieldCard__badge} ${styles['formFieldCard__badge--required']}`}>
            Zorunlu
          </span>
        )}
      </div>
    </div>
  );
};

export default FormFieldCard;