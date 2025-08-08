// path: frontend/src/components/formforgeapi/components/page-level/FormFillScreen.jsx
import React, { useEffect } from 'react';
import { useParams, useNavigate, Link, useLocation } from 'react-router-dom';
import { useForm, Controller } from 'react-hook-form';
import Select from 'react-select'; // react-select kütüphanesini import ediyoruz

// Custom Hooks
import useFormForgeApi from '../../hooks/useFormForgeApi';
import { useUserFormForgeApi } from '../../hooks/useUserFormForgeApi'; // Yeni hook'umuzu import ediyoruz

// Styles
import styles from '../../css/FormFillScreen.module.css';

const FormFillScreen = () => {
    // --- PARAMETRE VE NAVİGASYON ---
    const { formId, submissionId } = useParams();
    const navigate = useNavigate();
    const { state } = useLocation();
    const submissionToEdit = state?.submission;
    const isEditMode = !!submissionId;

    // --- HOOK'LARI HAZIRLAMA ---
    // 1. Ana form ve gönderim işlemleri için hook
    const {
        currentForm,
        loading: formLoading,
        error: formError,
        fetchForm,
        createSubmission,
        updateSubmission
    } = useFormForgeApi();

    // 2. Sadece kullanıcı listesi işlemleri için ayrılmış yeni hook
    const {
        userList,
        loading: usersLoading,
        fetchUserList
    } = useUserFormForgeApi();
    
    // 3. Form state yönetimi için react-hook-form
    const { control, handleSubmit, formState: { errors, isSubmitting }, reset } = useForm();

    // --- VERİ ÇEKME VE FORMU DOLDURMA ---
    useEffect(() => {
        // İster yeni form ister düzenleme modu olsun, kullanıcı listesini her zaman çekiyoruz.
        fetchUserList();
        
        if (isEditMode && submissionToEdit) {
            fetchForm(submissionToEdit.form);
        } else if (!isEditMode && formId) {
            fetchForm(formId);
        }
    }, [formId, submissionId, isEditMode, submissionToEdit, fetchForm, fetchUserList]);

    // Düzenleme modunda formu doldurmak için useEffect
    useEffect(() => {
        if (isEditMode && submissionToEdit) {
            const defaultValues = {};
            submissionToEdit.values.forEach(item => {
                defaultValues[`field_${item.form_field}`] = item.value;
            });
            reset(defaultValues);
        }
    }, [isEditMode, submissionToEdit, reset]);

    // --- FORM GÖNDERİM MANTIĞI ---
    const onSubmit = async (data) => {
        if (isEditMode) {
            await updateSubmission(submissionId, submissionToEdit.form, data);
        } else {
            await createSubmission(formId, data);
        }
        // Başarılı gönderim sonrası yönlendirme artık hook'un içinde yapılıyor.
    };

    // --- ALAN RENDER ETME FONKSİYONU ---
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
                        const commonProps = {
                            ...controllerField,
                            id: fieldName,
                            className: `${styles.formFillScreen__control} ${errors[fieldName] ? styles['formFillScreen__control--invalid'] : ''}`,
                        };
                        switch (field.field_type) {
                            case 'userpicker':
                                return (
                                    <Select
                                        inputId={fieldName}
                                        options={userList}
                                        isLoading={usersLoading}
                                        placeholder="Kullanıcı seçiniz..."
                                        onChange={(selectedOption) => controllerField.onChange(selectedOption ? selectedOption.value : null)}
                                        value={userList.find(c => c.value === controllerField.value) || null}
                                        onBlur={controllerField.onBlur}
                                        ref={controllerField.ref}
                                        isClearable
                                    />
                                );
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
                                                            const newValue = currentValue.includes(opt.label)
                                                                ? currentValue.filter(val => val !== opt.label)
                                                                : [...currentValue, opt.label];
                                                            controllerField.onChange(newValue);
                                                        }}
                                                        checked={currentValue.includes(opt.label)}
                                                    />
                                                    <label htmlFor={`${fieldName}-${opt.id}`}>{opt.label}</label>
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

    // --- ANA RENDER ---
    if (formLoading && !currentForm) return <div>Form Yükleniyor...</div>;
    if (formError) return <div className="alert alert-danger">Hata: {formError}</div>;
    if (!currentForm) return <div>Form bulunamadı.</div>;

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