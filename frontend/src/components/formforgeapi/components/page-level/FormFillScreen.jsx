// path: frontend/src/components/formforgeapi/components/page-level/FormFillScreen.jsx

import React, { useEffect } from 'react';
// DÜZELTME: Kütüphane adı doğru yazıldı.
import { useParams, useNavigate, Link } from 'react-router-dom';
import { useForm, Controller } from 'react-hook-form';
import useFormForgeApi from '../../hooks/useFormForgeApi';
import styles from '../../css/FormFillScreen.module.css';

const FormFillScreen = () => {
  const { formId } = useParams();
  const navigate = useNavigate();
  const { currentForm, loading, error, fetchForm, createSubmission } = useFormForgeApi();
  const { control, handleSubmit, formState: { errors, isSubmitting } } = useForm();

  useEffect(() => {
    if (formId) {
      fetchForm(formId);
    }
  }, [formId, fetchForm]);

  const onSubmit = async (data) => {
    await createSubmission(formId, data);
    navigate('/formforgeapi'); 
  };

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
              case 'textarea': return <textarea {...commonProps} />;
              case 'multiselect':
                return (
                  <select {...commonProps} multiple={true}>
                    {field.options.map(opt => <option key={opt.id} value={opt.label}>{opt.label}</option>)}
                  </select>
                );
              case 'singleselect':
                return (
                  <select {...commonProps}>
                    <option value="">Seçiniz...</option>
                    {field.options.map(opt => <option key={opt.id} value={opt.label}>{opt.label}</option>)}
                  </select>
                );
              case 'checkbox':
                 return ( <label><input type="checkbox" {...commonProps} checked={!!commonProps.value} /> {field.label}</label> );
              case 'radio':
                return field.options.map(opt => ( <label key={opt.id} className={styles.formFillScreen__inlineLabel}><input {...commonProps} type="radio" value={opt.label} /> {opt.label}</label> ));
              default:
                return <input type={field.field_type} {...commonProps} />;
            }
          }}
        />
        {errors[fieldId] && <p className={styles.formFillScreen__error}>{errors[fieldId].message}</p>}
      </div>
    );
  };

  if (loading && !currentForm) return <div>Form Yükleniyor...</div>;
  if (error) return <div className="alert alert-danger">Hata: {error}</div>;
  if (!currentForm) return <div>Form bulunamadı.</div>;

  return (
    <div className={styles.formFillScreen}>
      <div style={{ marginBottom: '1.5rem' }}>
        <Link to="/formforgeapi">&larr; Form Listesine Geri Dön</Link>
      </div>

      <h1 className={styles.formFillScreen__title}>{currentForm.title}</h1>
      {currentForm.description && (
        <p className={styles.formFillScreen__description}>{currentForm.description}</p>
      )}

      <form onSubmit={handleSubmit(onSubmit)} className={styles.formFillScreen__form}>
        {currentForm.fields.sort((a,b) => a.order - b.order).map(renderField)}
        <button type="submit" disabled={isSubmitting} className={styles.formFillScreen__submit}>
          {isSubmitting ? 'Gönderiliyor...' : 'Gönder'}
        </button>
      </form>
    </div>
  );
};

export default FormFillScreen;