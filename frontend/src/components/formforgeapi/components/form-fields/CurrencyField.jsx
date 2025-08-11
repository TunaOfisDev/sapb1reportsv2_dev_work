// path: frontend/src/components/formforgeapi/components/form-fields/CurrencyField.jsx

import React from 'react';
import { Controller } from 'react-hook-form';
import CurrencyInput from 'react-currency-input-field';
import styles from '../../css/form-fields.module.css';

/**
 * Para Birimi Alanı Bileşeni
 * --------------------------------------------------------------------
 * 'currency' tipindeki alanlar için 'react-currency-input-field' tabanlı,
 * otomatik formatlama yapan bir input render eder.
 *
 * @param {object} field - Render edilecek alanın şema bilgisi.
 * @param {object} control - react-hook-form'dan gelen kontrol nesnesi.
 * @param {object} errors - react-hook-form'dan gelen hata nesnesi.
 */
const CurrencyField = ({ field, control, errors }) => {
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
          <CurrencyInput
            id={fieldName}
            name={controllerField.name}
            value={controllerField.value}
            // Kütüphane, onValueChange ile temiz bir sayısal string döndürür.
            // Bu değeri doğrudan react-hook-form'un onChange'ine iletiyoruz.
            onValueChange={(value) => controllerField.onChange(value)}
            onBlur={controllerField.onBlur}
            ref={controllerField.ref}
            className={`${styles.fieldControl} ${errors[fieldName] ? styles['fieldControl--invalid'] : ''}`}
            placeholder={field.label}
            // Uluslararası formatlama ayarları.
            // Varsayılan olarak Türk Lirası ve formatını kullanır.
            intlConfig={{ locale: 'tr-TR', currency: 'TRY' }}
            decimalScale={2} // Ondalık basamak sayısı
          />
        )}
      />
      {errors[fieldName] && <p className={styles.errorMessage}>{errors[fieldName].message}</p>}
    </div>
  );
};

export default CurrencyField;