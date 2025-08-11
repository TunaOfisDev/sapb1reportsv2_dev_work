// path: frontend/src/components/formforgeapi/utils/UpdateSubmissionModal.jsx

import React, { useEffect } from 'react';
import { useForm } from 'react-hook-form';
import Modal from '../components/reusable/Modal'; // Kendi <Modal> bileşenimizi kullanıyoruz.
import FormFieldRenderer from '../components/form-fields/FormFieldRenderer'; // Akıllı yönlendiriciyi import ediyoruz.
import { useUserFormForgeApi } from '../hooks/useUserFormForgeApi'; // Kullanıcı listesi için
import styles from '../css/UpdateSubmissionModal.module.css'; // Mevcut CSS'i kullanmaya devam ediyoruz

const UpdateSubmissionModal = ({ isOpen, onClose, submission, formSchema, onUpdate }) => {
  // --- HOOK'LARI HAZIRLAMA ---
  const { 
    control, handleSubmit, 
    formState: { errors, isSubmitting }, 
    reset, watch, setValue 
  } = useForm();
  
  // 'userpicker' gibi alanları beslemek için kullanıcı listesini çekiyoruz
  const { userList, loading: usersLoading, fetchUserList } = useUserFormForgeApi();

  // --- VERİ ÇEKME VE FORMU DOLDURMA ---
  useEffect(() => {
    // Modal her açıldığında kullanıcı listesini çek
    if (isOpen) {
      fetchUserList();
    }
  }, [isOpen, fetchUserList]);

  useEffect(() => {
    // Gönderim verisi değiştiğinde veya modal açıldığında formu doldur
    if (submission && isOpen) {
      const defaultValues = {};
      submission.values.forEach(item => {
        // userpicker gibi obje değerlerini doğru almak için
        const value = (typeof item.value === 'object' && item.value !== null && 'id' in item.value) 
          ? item.value.id 
          : item.value;
        defaultValues[`field_${item.form_field}`] = value;
      });
      reset(defaultValues);
    }
  }, [submission, isOpen, reset]);

  // --- FORM GÖNDERİM MANTIĞI ---
  const onSubmit = async (data) => {
    await onUpdate(submission.id, submission.form, data);
    onClose(); // İşlem bitince modalı kapat
  };
  
  if (!isOpen) return null;

  return (
    <Modal isOpen={isOpen} onClose={onClose} title={`Kaydı Düzenle (ID: ${submission.id}, V${submission.version})`}>
      <form onSubmit={handleSubmit(onSubmit)} className={styles.updateModal__formContainer}>
        {/*
          DEĞİŞİKLİK: Modalın gövdesi artık kaydırılabilir. 
          Eski devasa switch-case yapısı yerine tek bir FormFieldRenderer kullanıyoruz.
        */}
        <div className={styles.updateModal__body}>
          {formSchema?.fields.sort((a, b) => a.order - b.order).map(field => (
            <FormFieldRenderer
              key={field.id}
              field={field}
              control={control}
              errors={errors}
              userList={userList}
              usersLoading={usersLoading}
              watch={watch}
              setValue={setValue}
            />
          ))}
        </div>

        {/* Footer, gövdeden ayrı olduğu için her zaman görünür olacak */}
        <div className={styles.updateModal__footer}>
          <button 
            type="button" 
            className={`${styles.updateModal__button} ${styles.updateModal__button_secondary}`} 
            onClick={onClose}
          >
            İptal
          </button>
          <button 
            type="submit" 
            className={`${styles.updateModal__button} ${styles.updateModal__button_primary}`} 
            disabled={isSubmitting}
          >
            {isSubmitting ? 'Kaydediliyor...' : 'Değişiklikleri Kaydet'}
          </button>
        </div>
      </form>
    </Modal>
  );
};

export default UpdateSubmissionModal;