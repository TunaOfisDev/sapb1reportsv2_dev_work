// path: frontend/src/components/formforgeapi/components/page-level/FormFillScreen.jsx
import React, { useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useForm, Controller } from 'react-hook-form';
import useFormForgeApi from '../../hooks/useFormForgeApi';
import styles from '../../css/FormFillScreen.module.css';

/**
 * FormFillScreen Bileşeni
 * --------------------------------------------------------------------
 * Son kullanıcının dinamik bir formu doldurup gönderdiği sayfa.
 *
 * Mimarideki Yeri:
 * - "Aptal" bir sayfa bileşenidir.
 * - `useParams` ile URL'den form ID'sini alır.
 * - Form şemasını getirmek (`fetchForm`) ve veriyi göndermek (`createSubmission`)
 * için `useFormForgeApi` hook'unu kullanır.
 * - Form state'ini ve doğrulamayı yönetmek için `react-hook-form` kullanır.
 *
 * İş Akışı:
 * 1. URL'den `formId` alınır.
 * 2. `useEffect` ile `fetchForm(formId)` çağrılarak form şeması yüklenir.
 * 3. Şema yüklendiğinde, `currentForm.fields` dizisi map'lenerek her alan
 * için `Controller` bileşeni ile bir form elemanı render edilir.
 * 4. Kullanıcı formu doldurup gönderdiğinde, `react-hook-form` veriyi toplar
 * ve `createSubmission` fonksiyonu ile API'ye gönderir.
 */
const FormFillScreen = () => {
  const { formId } = useParams();
  const navigate = useNavigate();
  const { currentForm, loading, error, fetchForm, createSubmission } = useFormForgeApi();
  const { control, handleSubmit, formState: { errors, isSubmitting } } = useForm();

  useEffect(() => {
    if (formId) {
      fetchForm(formId);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [formId]);

  const onSubmit = async (data) => {
    // `useFormForgeApi` hook'u veriyi backend'in beklediği
    // nested formata çevirecek şekilde tasarlanmıştı.
    await createSubmission(formId, data);
    // Başarılı gönderim sonrası kullanıcıyı başka bir sayfaya yönlendir.
    navigate('/formforgeapi/forms'); // Veya bir "Teşekkürler" sayfasına
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

  if (loading && !currentForm) return <div>Form Yükleniyor...</div>;
  if (error) return <div className="alert alert-danger">Hata: {error}</div>;
  if (!currentForm) return <div>Form bulunamadı.</div>;

  return (
    <div className={styles.formFillScreen}>
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