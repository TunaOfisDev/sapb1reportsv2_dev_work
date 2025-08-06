// YENİ DOSYA: frontend/src/components/formforgeapi/components/canvas/FormPreview.jsx

import React from 'react';
import { Controller } from 'react-hook-form';
import useFormForgePreview from '../../hooks/useFormForgePreview';
import styles from '../../css/FormFillScreen.module.css'; // FormFillScreen stillerini kullanabiliriz

const FormPreview = ({ form }) => {
  // Bu hook, react-hook-form'u bizim için yönetir
  const { control, errors, handlePreviewSubmit } = useFormForgePreview(form);

  const renderField = (field) => {
    const fieldId = String(field.id);
    return (
      <div key={fieldId} className={styles.formFillScreen__group}>
        <label htmlFor={fieldId} className={styles.formFillScreen__label}>
          {field.label} {field.is_required && '*'}
        </label>
        <Controller
          name={fieldId}
          control={control}
          rules={{ required: field.is_required ? 'Bu alan zorunludur.' : false }}
          render={({ field: controllerField }) => {
            const commonProps = {
              ...controllerField,
              id: fieldId,
              className: `${styles.formFillScreen__control} ${errors[fieldId] ? styles['formFillScreen__control--invalid'] : ''}`,
            };
            switch (field.field_type) {
              case 'textarea':
                return <textarea {...commonProps} />;
              case 'singleselect':
                return (
                  <select {...commonProps}>
                    <option value="">Seçiniz...</option>
                    {field.options.map(opt => <option key={opt.id} value={opt.label}>{opt.label}</option>)}
                  </select>
                );
              case 'checkbox':
                 return (
                    <label className={styles.formFillScreen__inlineLabel}>
                        <input type="checkbox" {...commonProps} checked={!!commonProps.value} />
                        {field.label}
                    </label>
                 );
              case 'radio':
                return field.options.map(opt => (
                    <label key={opt.id} className={styles.formFillScreen__inlineLabel}>
                        <input {...commonProps} type="radio" value={opt.label} />
                        {opt.label}
                    </label>
                ));
              default: // text, number, email, date
                return <input type={field.field_type} {...commonProps} />;
            }
          }}
        />
        {errors[fieldId] && <p className={styles.formFillScreen__error}>{errors[fieldId].message}</p>}
      </div>
    );
  };
  
  if (!form?.fields) {
    return <p>Önizleme için forma alan ekleyin.</p>
  }

  return (
    <div className={styles.formFillScreen} style={{background: 'white', padding: '2rem'}}>
      <form onSubmit={handlePreviewSubmit} className={styles.formFillScreen__form}>
        {form.fields.sort((a, b) => a.order - b.order).map(renderField)}
        <button type="submit" className={styles.formFillScreen__submit}>
          Gönder (Önizleme)
        </button>
      </form>
    </div>
  );
};

export default FormPreview;