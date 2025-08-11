// path: frontend/src/components/formforgeapi/components/form-fields/CalculatedField.jsx

import React, { useEffect } from 'react';
import { Controller } from 'react-hook-form';
import styles from '../../css/form-fields.module.css';

// Güvenli bir şekilde matematiksel ifadeyi çözen basit bir fonksiyon
// Not: Bu fonksiyon sadece temel dört işlemi destekler ve güvenlik için `eval` kullanmaz.
const safeCalculate = (formula, values) => {
  try {
    const expression = formula.replace(/\{field_(\d+)\}/g, (match, fieldId) => {
      // Değeri al, sayı değilse veya boşsa 0 olarak kabul et
      const val = parseFloat(values[`field_${fieldId}`]);
      return isNaN(val) ? 0 : val;
    });

    // Sadece izin verilen karakterlerin olduğundan emin ol (güvenlik)
    if (!/^[0-9+\-*/.() ]+$/.test(expression)) {
      return 'Geçersiz Formül';
    }
    
    // Güvenli bir şekilde hesaplama yapmak için Function constructor'ı kullan
    return new Function(`return ${expression}`)();
  } catch (error) {
    return 'Hesaplama Hatası';
  }
};


const CalculatedField = ({ field, control, errors, watch, setValue }) => {
  const fieldName = `field_${field.id}`;
  
  // ÖNEMLİ NOT: Bu formülün backend'den gelmesi gerekecek.
  // Şimdilik test amaçlı bir formül varsayalım.
  const formula = field.calculation_formula || "0";

  // Formüldeki tüm alan ID'lerini bul (örn: ["field_1", "field_2"])
  const watchedFieldNames = [...formula.matchAll(/\{field_(\d+)\}/g)].map(match => `field_${match[1]}`);

  // Bulunan alanları izle
  const watchedValues = watch(watchedFieldNames);

  useEffect(() => {
    // İzlenen alanlardan herhangi biri değiştiğinde bu kod çalışır.
    const allWatchedValues = watch(); // Tüm form verilerini al
    const result = safeCalculate(formula, allWatchedValues);

    // Hesaplanan sonucu react-hook-form state'ine yaz.
    // `shouldValidate: true` ile bu alanın da doğrulama tetiklemesini sağlayabiliriz.
    setValue(fieldName, result, { shouldDirty: true, shouldTouch: true });

  }, [watchedValues, formula, fieldName, setValue, watch]);

  return (
    <div className={styles.fieldGroup}>
      <label htmlFor={fieldName} className={styles.fieldLabel}>
        {field.label}
      </label>
      <Controller
        name={fieldName}
        control={control}
        render={({ field: controllerField }) => (
          <input
            {...controllerField}
            id={fieldName}
            type="text"
            className={`${styles.fieldControl} ${styles.calculatedField}`}
            readOnly // Kullanıcı bu alanı değiştiremez
          />
        )}
      />
      {errors[fieldName] && <p className={styles.errorMessage}>{errors[fieldName].message}</p>}
    </div>
  );
};

export default CalculatedField;