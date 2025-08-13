// path: frontend/src/components/formforgeapi/components/form-fields/PhoneField.jsx

import React from 'react';
import { Controller } from 'react-hook-form';
import PhoneInput from 'react-phone-number-input';
import 'react-phone-number-input/style.css'; // Kütüphanenin kendi stillerini import ediyoruz
import styles from '../../css/form-fields.module.css';

/**
 * Telefon Numarası Alanı Bileşeni
 * --------------------------------------------------------------------
 * 'phone' tipindeki alanlar için 'react-phone-number-input' tabanlı,
 * ülke kodu seçimi ve formatlama özellikli bir input render eder.
 *
 * @param {object} field - Render edilecek alanın şema bilgisi.
 * @param {object} control - react-hook-form'dan gelen kontrol nesnesi.
 * @param {object} errors - react-hook-form'dan gelen hata nesnesi.
 */
const PhoneField = ({ field, control, errors }) => {
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
          // Hata durumunda çerçeve rengini değiştirebilmek için bir sarmalayıcı kullanıyoruz.
          <div className={`${styles.phoneInputWrapper} ${errors[fieldName] ? styles['phoneInputWrapper--invalid'] : ''}`}>
            <PhoneInput
              id={fieldName}
              {...controllerField}
              defaultCountry="TR" // Varsayılan ülke olarak Türkiye'yi ayarla
              placeholder={field.label}
              className={styles.phoneInput} // Kendi iç input'una stil vermek için (opsiyonel)
            />
          </div>
        )}
      />
      {errors[fieldName] && <p className={styles.errorMessage}>{errors[fieldName].message}</p>}
    </div>
  );
};

export default PhoneField;