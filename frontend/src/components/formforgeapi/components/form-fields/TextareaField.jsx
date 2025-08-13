// frontend/src/components/formforgeapi/components/form-fields/TextareaField.jsx
import React from 'react';
import { Controller } from 'react-hook-form';
import styles from '../../css/form-fields.module.css';

/**
 * Çok Satırlı Metin Alanı (Textarea) Bileşeni
 * --------------------------------------------------------------------
 * 'textarea' tipindeki alanlar için bir <textarea> elementi render eder.
 *
 * @param {object} field - Render edilecek alanın şema bilgisi.
 * @param {object} control - react-hook-form'dan gelen kontrol nesnesi.
 * @param {object} errors - react-hook-form'dan gelen hata nesnesi.
 */
const TextareaField = ({ field, control, errors }) => {
  const fieldName = `field_${field.id}`;

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
          <textarea
            {...controllerField}
            id={fieldName}
            rows="4" // Varsayılan satır yüksekliği
            className={`${styles.fieldControl} ${errors[fieldName] ? styles['fieldControl--invalid'] : ''}`}
            placeholder={field.label}
          />
        )}
      />
      {errors[fieldName] && <p className={styles.errorMessage}>{errors[fieldName].message}</p>}
    </div>
  );
};

export default TextareaField;