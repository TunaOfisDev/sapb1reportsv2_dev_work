// path: frontend/src/components/formforgeapi/components/form-fields/RatingField.jsx

import React, { useState } from 'react';
import { Controller } from 'react-hook-form';
import styles from '../../css/form-fields.module.css';

/**
 * Derecelendirme (Yıldız) Alanı Bileşeni
 * --------------------------------------------------------------------
 * 'rating' tipindeki alanlar için 1-5 arası tıklanabilir yıldız render eder.
 *
 * @param {object} field - Render edilecek alanın şema bilgisi.
 * @param {object} control - react-hook-form'dan gelen kontrol nesnesi.
 * @param {object} errors - react-hook-form'dan gelen hata nesnesi.
 */
const RatingField = ({ field, control, errors }) => {
  const fieldName = `field_${field.id}`;
  // Fareyle üzerine gelme (hover) durumunu yönetmek için yerel state
  const [hoverRating, setHoverRating] = useState(0);

  return (
    <div className={styles.fieldGroup}>
      <label className={styles.fieldLabel}>
        {field.label}
        {field.is_required && <span className={styles.fieldLabel__required}>*</span>}
      </label>
      <Controller
        name={fieldName}
        control={control}
        rules={{ required: field.is_required ? 'Bu alan zorunludur.' : false }}
        render={({ field: controllerField }) => (
          <div
            className={styles.ratingContainer}
            onMouseLeave={() => setHoverRating(0)} // Fare konteynerdan ayrılınca hover'ı sıfırla
          >
            {[1, 2, 3, 4, 5].map((starValue) => {
              // Yıldızın dolu olup olmadığını belirle:
              // Önce hover durumuna bak, hover yoksa kayıtlı değere bak.
              const isFilled = starValue <= (hoverRating || controllerField.value);
              return (
                <span
                  key={starValue}
                  className={`${styles.ratingStar} ${isFilled ? styles['ratingStar--filled'] : ''}`}
                  onMouseEnter={() => setHoverRating(starValue)}
                  onClick={() => controllerField.onChange(starValue)}
                >
                  ★
                </span>
              );
            })}
          </div>
        )}
      />
      {errors[fieldName] && <p className={styles.errorMessage}>{errors[fieldName].message}</p>}
    </div>
  );
};

export default RatingField;