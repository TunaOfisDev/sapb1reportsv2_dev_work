// path: frontend/src/components/formforgeapi/components/page-level/FormFillScreen.jsx

import React, { useEffect } from 'react';
// GÜNCELLEME: `useLocation` hook'u eklendi
import { useParams, useNavigate, Link, useLocation } from 'react-router-dom';
import { useForm, Controller } from 'react-hook-form';
import useFormForgeApi from '../../hooks/useFormForgeApi';
import styles from '../../css/FormFillScreen.module.css';

const FormFillScreen = () => {
  // --- MOD TESPİTİ VE VERİ ALMA ---
  const { formId, submissionId } = useParams();
  const navigate = useNavigate();
  const { state } = useLocation(); // Bir önceki sayfadan gönderilen veriyi almak için
  const submissionToEdit = state?.submission; // state içindeki submission verisi
  const isEditMode = !!submissionId; // submissionId varsa, düzenleme modundayız.

  // --- HOOK'LARI HAZIRLAMA ---
  // GÜNCELLEME: `updateSubmission` fonksiyonunu da hook'tan alıyoruz
  const { currentForm, loading, error, fetchForm, createSubmission, updateSubmission } = useFormForgeApi();
  // `reset` fonksiyonunu da alıyoruz, formu doldurmak için kullanacağız
  const { control, handleSubmit, formState: { errors, isSubmitting }, reset } = useForm();

  // --- VERİ ÇEKME VE FORMU DOLDURMA ---
  useEffect(() => {
    // Düzenleme modunda, gönderim verisi içindeki form ID'si ile form şemasını çek
    if (isEditMode && submissionToEdit) {
      fetchForm(submissionToEdit.form);
    } 
    // Oluşturma modunda, URL'deki form ID'si ile form şemasını çek
    else if (!isEditMode && formId) {
      fetchForm(formId);
    }
  }, [formId, submissionId, isEditMode, submissionToEdit, fetchForm]);

  // Düzenleme modundaysak ve gönderim verisi mevcutsa, formu bu verilerle doldur
  useEffect(() => {
    if (isEditMode && submissionToEdit) {
      // react-hook-form'un anlayacağı formata çeviriyoruz: { field_1: 'değer', field_2: ['değerA'] }
      const defaultValues = {};
      submissionToEdit.values.forEach(item => {
        defaultValues[`field_${item.form_field}`] = item.value;
      });
      reset(defaultValues); // `reset` metodu ile formu doldur
    }
  }, [isEditMode, submissionToEdit, reset]);

  // --- FORM GÖNDERİM MANTIĞI ---
  const onSubmit = async (data) => {
    // GÜNCELLEME: Moda göre doğru fonksiyonu çağır
    if (isEditMode) {
      await updateSubmission(submissionId, submissionToEdit.form, data);
    } else {
      await createSubmission(formId, data);
    }
  };

  const renderField = (field) => {
    const fieldName = `field_${field.id}`;
    return (
      <div key={field.id} className={styles.formFillScreen__group}>
        <label htmlFor={fieldName} className={styles.formFillScreen__label}>
          {field.label} {field.is_required && '*'}
        </label>
        <Controller
          name={fieldName}
          control={control}
          rules={{ required: field.is_required ? 'Bu alan zorunludur.' : false }}
          render={({ field: controllerField }) => {
            // ... (renderField içindeki switch-case yapısı aynı kalacak) ...
            const commonProps = {
                ...controllerField,
                id: fieldName,
                className: `${styles.formFillScreen__control} ${errors[fieldName] ? styles['formFillScreen__control--invalid'] : ''}`,
            };
            switch (field.field_type) {
                case 'textarea': 
                return <textarea {...commonProps} />;
                
                case 'multiselect':
                return (
                    <div className={styles.formFillScreen__checkboxGroup}>
                    {field.options.map(opt => {
                        const currentValue = controllerField.value || [];
                        return (
                        <div className={styles.formFillScreen__checkItem} key={opt.id}>
                            <input
                            type="checkbox"
                            id={`${fieldName}-${opt.id}`}
                            onBlur={controllerField.onBlur}
                            onChange={() => {
                                let newValue;
                                if (currentValue.includes(opt.label)) {
                                newValue = currentValue.filter(val => val !== opt.label);
                                } else {
                                newValue = [...currentValue, opt.label];
                                }
                                controllerField.onChange(newValue);
                            }}
                            checked={currentValue.includes(opt.label)}
                            />
                            <label htmlFor={`${fieldName}-${opt.id}`}>
                            {opt.label}
                            </label>
                        </div>
                        );
                    })}
                    </div>
                );
                case 'singleselect':
                return (
                    <select {...commonProps}>
                    <option value="">Seçiniz...</option>
                    {field.options.map(opt => <option key={opt.id} value={opt.label}>{opt.label}</option>)}
                    </select>
                );
                default:
                return <input type={field.field_type} {...commonProps} />;
            }
          }}
        />
        {errors[fieldName] && <p className={styles.formFillScreen__error}>{errors[fieldName].message}</p>}
      </div>
    );
  };

  if (loading && !currentForm) return <div>Form Yükleniyor...</div>;
  if (error) return <div className="alert alert-danger">Hata: {error}</div>;
  if (!currentForm) return <div>Form bulunamadı veya düzenlenecek gönderi bilgisi eksik.</div>;

  return (
    <div className={styles.formFillScreen}>
      <div style={{ marginBottom: '1.5rem' }}>
        <Link to={isEditMode ? `/formforgeapi/data/${submissionToEdit.form}` : "/formforgeapi"}>
          &larr; {isEditMode ? 'Veri Listesine Geri Dön' : 'Form Listesine Geri Dön'}
        </Link>
      </div>

      <h1 className={styles.formFillScreen__title}>
        {isEditMode ? `${currentForm.title} - Kaydını Düzenle` : currentForm.title}
      </h1>
      {currentForm.description && (
        <p className={styles.formFillScreen__description}>{currentForm.description}</p>
      )}

      <form onSubmit={handleSubmit(onSubmit)} className={styles.formFillScreen__form}>
        {currentForm.fields.sort((a,b) => a.order - b.order).map(renderField)}
        <button type="submit" disabled={isSubmitting} className={styles.formFillScreen__submit}>
          {isSubmitting ? 'Kaydediliyor...' : (isEditMode ? 'Güncelle' : 'Gönder')}
        </button>
      </form>
    </div>
  );
};

export default FormFillScreen;