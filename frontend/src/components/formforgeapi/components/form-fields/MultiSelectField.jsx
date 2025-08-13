// path: frontend/src/components/formforgeapi/components/form-fields/MultiSelectField.jsx

import React from 'react';
import { Controller } from 'react-hook-form';
import styles from '../../css/form-fields.module.css';

/**
 * Çoklu Seçim (Checkbox Grubu) Alanı Bileşeni
 * --------------------------------------------------------------------
 * 'multiselect' tipindeki alanlar için bir grup checkbox render eder.
 * Seçilen değerleri bir dizi olarak yönetir.
 *
 * @param {object} field - Render edilecek alanın şema bilgisi.
 * @param {object} control - react-hook-form'dan gelen kontrol nesnesi.
 * @param {object} errors - react-hook-form'dan gelen hata nesnesi.
 */
const MultiSelectField = ({ field, control, errors }) => {
  const fieldName = `field_${field.id}`;

  return (
    <div className={styles.fieldGroup}>
      <label className={styles.fieldLabel}>
        {field.label}
        {field.is_required && <span className={styles.fieldLabel__required}>*</span>}
      </label>
      <Controller
        name={fieldName}
        control={control}
        rules={{ 
          required: field.is_required ? 'En az bir seçenek işaretlenmelidir.' : false 
        }}
        render={({ field: controllerField }) => (
          <div className={styles.checkboxGroupContainer}>
            {(field.options || []).map(option => {
              // controllerField.value'nun her zaman bir dizi olduğundan emin ol
              const currentValue = controllerField.value || [];
              return (
                <div key={option.id} className={styles.checkItem}>
                  <input
                    type="checkbox"
                    id={`${fieldName}-${option.id}`}
                    onBlur={controllerField.onBlur}
                    // Checkbox'ın durumu değiştiğinde...
                    onChange={() => {
                      let newValue;
                      if (currentValue.includes(option.label)) {
                        // Eğer zaten seçiliyse, diziden çıkar
                        newValue = currentValue.filter(val => val !== option.label);
                      } else {
                        // Eğer seçili değilse, diziye ekle
                        newValue = [...currentValue, option.label];
                      }
                      controllerField.onChange(newValue);
                    }}
                    // Değeri dizide varsa, 'checked' olarak işaretle
                    checked={currentValue.includes(option.label)}
                  />
                  <label htmlFor={`${fieldName}-${option.id}`}>
                    {option.label}
                  </label>
                </div>
              );
            })}
          </div>
        )}
      />
      {errors[fieldName] && <p className={styles.errorMessage}>{errors[fieldName].message}</p>}
    </div>
  );
};

export default MultiSelectField;