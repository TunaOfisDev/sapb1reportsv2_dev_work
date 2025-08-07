// path: frontend/src/components/formforgeapi/utils/UpdateSubmissionModal.jsx

import React, { useEffect } from 'react';
import ReactDOM from 'react-dom';
import { useForm, Controller } from 'react-hook-form';
import styles from '../css/UpdateSubmissionModal.module.css';

const UpdateSubmissionModal = ({ isOpen, onClose, submission, formSchema, onUpdate }) => {
  const { control, handleSubmit, formState: { errors, isSubmitting }, reset } = useForm();

  useEffect(() => {
    if (submission) {
      const defaultValues = {};
      submission.values.forEach(item => {
        defaultValues[`field_${item.form_field}`] = item.value;
      });
      reset(defaultValues);
    }
  }, [submission, isOpen, reset]);

  const onSubmit = async (data) => {
    await onUpdate(submission.id, submission.form, data);
    onClose();
  };
  
  if (!isOpen) return null;

  return ReactDOM.createPortal(
    <div className={`${styles.updateModal__overlay} ${isOpen ? styles.updateModal__overlay_open : ''}`} onMouseDown={onClose}>
      <div className={styles.updateModal} onMouseDown={(e) => e.stopPropagation()}>
        <form onSubmit={handleSubmit(onSubmit)}>
          <div className={styles.updateModal__header}>
            <h5 className={styles.updateModal__title}>Kaydı Düzenle (ID: {submission.id}, V{submission.version})</h5>
            <button type="button" className={styles.updateModal__closeButton} onClick={onClose}>&times;</button>
          </div>

          <div className={styles.updateModal__body}>
            <div className={styles.updateModal__form}>
              {formSchema?.fields.sort((a,b) => a.order - b.order).map(field => {
                const fieldName = `field_${field.id}`;
                return (
                  <div key={field.id} className={styles.updateModal__formGroup}>
                    <label htmlFor={fieldName} className={styles.updateModal__label}>
                      {field.label} {field.is_required && <span style={{color: 'red'}}>*</span>}
                    </label>
                    <Controller
                      name={fieldName}
                      control={control}
                      rules={{ required: field.is_required ? 'Bu alan zorunludur.' : false }}
                      render={({ field: controllerField }) => {
                        const commonProps = {
                          ...controllerField,
                          id: fieldName,
                          className: `${styles.updateModal__control} ${errors[fieldName] ? styles.updateModal__control_invalid : ''}`,
                        };
                        switch (field.field_type) {
                          case 'textarea': return <textarea {...commonProps} rows="4" />;
                          case 'multiselect':
                            return (
                              <div className={styles.updateModal__checkboxGroup}>
                                {field.options.map(opt => {
                                  const currentValue = controllerField.value || [];
                                  return (
                                    <div className={styles.updateModal__checkItem} key={opt.id}>
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
                    {errors[fieldName] && <p className={styles.updateModal__error}>{errors[fieldName].message}</p>}
                  </div>
                );
              })}
            </div>
          </div>

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
      </div>
    </div>,
    document.body
  );
};

export default UpdateSubmissionModal;