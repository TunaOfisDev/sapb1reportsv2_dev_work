// path: frontend/src/components/formforgeapi/components/page-level/FormFillScreen.jsx

import React, { useEffect } from 'react';
import { useParams, useNavigate, Link, useLocation } from 'react-router-dom';
import { useForm } from 'react-hook-form';

// Custom Hooks
import useFormForgeApi from '../../hooks/useFormForgeApi';
import { useUserFormForgeApi } from '../../hooks/useUserFormForgeApi';

// Componentler
import FormFieldRenderer from '../form-fields/FormFieldRenderer';

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
    const {
        currentForm, loading: formLoading, error: formError,
        fetchForm, createSubmission, updateSubmission
    } = useFormForgeApi();

    const {
        userList, loading: usersLoading, fetchUserList
    } = useUserFormForgeApi();
    
    const { control, handleSubmit, formState: { errors, isSubmitting }, reset } = useForm();

    // --- VERİ ÇEKME VE FORMU DOLDURMA ---
    useEffect(() => {
        fetchUserList();
        
        if (isEditMode && submissionToEdit) {
            fetchForm(submissionToEdit.form);
        } else if (!isEditMode && formId) {
            fetchForm(formId);
        }
    }, [formId, submissionId, isEditMode, submissionToEdit, fetchForm, fetchUserList]);

    useEffect(() => {
        if (isEditMode && submissionToEdit) {
            const defaultValues = {};
            submissionToEdit.values.forEach(item => {
                const value = (typeof item.value === 'object' && item.value !== null) ? item.value.id : item.value;
                defaultValues[`field_${item.form_field}`] = value;
            });
            reset(defaultValues);
        }
    }, [isEditMode, submissionToEdit, reset]);

    // --- GÜVENLİ FORM GÖNDERİM MANTIĞI ---
    const onSubmit = (data) => {
        const handleAsyncSubmit = async () => {
            try {
                if (isEditMode) {
                    await updateSubmission(submissionId, submissionToEdit.form, data);
                } else {
                    await createSubmission(formId, data);
                }
            } catch (error) {
                console.error("Form gönderim fonksiyonunda hata yakalandı:", error);
            }
        };
        handleAsyncSubmit();
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
                {currentForm.fields
                    .sort((a, b) => a.order - b.order)
                    .map(field => (
                        <FormFieldRenderer
                            key={field.id}
                            field={field}
                            control={control}
                            errors={errors}
                            userList={userList}
                            usersLoading={usersLoading}
                        />
                    ))
                }
                <button type="submit" disabled={isSubmitting} className={styles.formFillScreen__submit}>
                    {isSubmitting ? 'Kaydediliyor...' : (isEditMode ? 'Güncelle' : 'Gönder')}
                </button>
            </form>
        </div>
    );
};

export default FormFillScreen;