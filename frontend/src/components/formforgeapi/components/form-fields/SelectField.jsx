// frontend/src/components/formforgeapi/components/form-fields/SelectField.jsx
import React from 'react';
import { Controller } from 'react-hook-form';
import styles from '../../css/form-fields.module.css';

/**
 * Tekli Seçim (Dropdown) Alanı Bileşeni
 * --------------------------------------------------------------------
 * 'singleselect' tipindeki alanlar için bir <select> elementi render eder.
 * Seçenekleri 'field.options' dizisinden alır.
 *
 * @param {object} field - Render edilecek alanın şema bilgisi.
 * @param {object} control - react-hook-form'dan gelen kontrol nesnesi.
 * @param {object} errors - react-hook-form'dan gelen hata nesnesi.
 */
const SelectField = ({ field, control, errors }) => {
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
          <select
            {...controllerField}
            id={fieldName}
            className={`${styles.fieldControl} ${errors[fieldName] ? styles['fieldControl--invalid'] : ''}`}
          >
            <option value="">Seçiniz...</option>
            {/* field.options dizisindeki her bir eleman için bir <option> oluştur */}
            {(field.options || []).map(option => (
              <option key={option.id} value={option.label}>
                {option.label}
              </option>
            ))}
          </select>
        )}
      />
      {errors[fieldName] && <p className={styles.errorMessage}>{errors[fieldName].message}</p>}
    </div>
  );
};

export default SelectField;