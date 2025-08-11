// frontend/src/components/formforgeapi/components/form-fields/TextField.jsx
import React from 'react';
import { Controller } from 'react-hook-form';
import styles from '../../css/form-fields.module.css';

// Alan tipine göre doğru HTML input tipini döndüren yardımcı fonksiyon
const mapFieldTypeToInputType = (fieldType) => {
  switch (fieldType) {
    case 'email': return 'email';
    case 'number': return 'number';
    case 'url': return 'url';
    case 'phone': return 'tel';
    // Para birimi ve yüzde için şimdilik 'text' kullanıyoruz,
    // Faz 2'de özel maskeleme kütüphaneleri ekleyeceğiz.
    case 'currency':
    case 'percentage':
    default:
      return 'text';
  }
};

const TextField = ({ field, control, errors }) => {
  const fieldName = `field_${field.id}`;
  const inputType = mapFieldTypeToInputType(field.field_type);

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
            placeholder={field.label}
          />
        )}
      />
      {errors[fieldName] && <p className={styles.errorMessage}>{errors[fieldName].message}</p>}
    </div>
  );
};

export default TextField;