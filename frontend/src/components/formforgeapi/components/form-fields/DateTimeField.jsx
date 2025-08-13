// frontend/src/components/formforgeapi/components/form-fields/DateTimeField.jsx
import React from 'react';
import { Controller } from 'react-hook-form';
import styles from '../../css/form-fields.module.css';

// Alan tipine göre doğru HTML input tipini döndüren yardımcı fonksiyon
const mapToInputType = (fieldType) => {
  switch (fieldType) {
    case 'datetime':
      return 'datetime-local'; // HTML5 standardı
    case 'time':
      return 'time';
    case 'date':
    default:
      return 'date';
  }
};

const DateTimeField = ({ field, control, errors }) => {
  const fieldName = `field_${field.id}`;
  const inputType = mapToInputType(field.field_type);

  return (
    <div className={styles.fieldGroup}>
      <label htmlFor={fieldName} className={styles.fieldLabel}>
        {field.label}
        {field.is_required && <span className={styles.fieldLabel__required}>*</span>}
      </label>
      <Controller
        name={fieldName}
        control={control}
        rules={{ required: field.is_required ? 'Bu alan zorunludur.' : false }}
        render={({ field: controllerField }) => (
          <input
            {...controllerField}
            id={fieldName}
            type={inputType}
            className={`${styles.fieldControl} ${errors[fieldName] ? styles['fieldControl--invalid'] : ''}`}
          />
        )}
      />
      {errors[fieldName] && <p className={styles.errorMessage}>{errors[fieldName].message}</p>}
    </div>
  );
};

export default DateTimeField;