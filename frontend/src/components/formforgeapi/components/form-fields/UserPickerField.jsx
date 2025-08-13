// path: frontend/src/components/formforgeapi/components/form-fields/UserPickerField.jsx

import React from 'react';
import { Controller } from 'react-hook-form';
import Select from 'react-select';
import styles from '../../css/form-fields.module.css';

/**
 * Kullanıcı Seçim Alanı (User Picker) Bileşeni
 * --------------------------------------------------------------------
 * 'userpicker' tipindeki alanlar için 'react-select' tabanlı,
 * aranabilir bir dropdown render eder.
 *
 * @param {object} field - Render edilecek alanın şema bilgisi.
 * @param {object} control - react-hook-form'dan gelen kontrol nesnesi.
 * @param {object} errors - react-hook-form'dan gelen hata nesnesi.
 * @param {Array} userList - react-select için formatlanmış kullanıcı listesi.
 * @param {boolean} isLoading - Kullanıcı listesinin yüklenip yüklenmediği.
 */
const UserPickerField = ({ field, control, errors, userList, isLoading }) => {
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
          <Select
            inputId={fieldName}
            options={userList}
            isLoading={isLoading}
            placeholder="Kullanıcı ara veya seç..."
            isClearable
            // react-select, seçilen option'ın tamamını (obje) döndürür.
            // Biz react-hook-form'a sadece ID'sini (value) kaydetmek istiyoruz.
            onChange={(selectedOption) => controllerField.onChange(selectedOption ? selectedOption.value : null)}
            // react-hook-form'da kayıtlı olan ID'ye göre listeden tam option objesini bulup
            // react-select'e 'value' olarak veriyoruz.
            value={userList.find(opt => opt.value === controllerField.value) || null}
            onBlur={controllerField.onBlur}
            ref={controllerField.ref}
            noOptionsMessage={() => "Kullanıcı bulunamadı."}
            loadingMessage={() => "Kullanıcılar yükleniyor..."}
            // İsteğe bağlı: react-select stillerini özelleştirebilirsin
            // styles={{ control: (base) => ({ ...base, ... }) }}
          />
        )}
      />
      {errors[fieldName] && <p className={styles.errorMessage}>{errors[fieldName].message}</p>}
    </div>
  );
};

export default UserPickerField;