// path: frontend/src/components/formforgeapi/components/canvas/FormPreview.jsx

import React from 'react';
import styles from '../../css/FormFillScreen.module.css'; // Stil için FormFillScreen'in CSS'ini kullanıyoruz.
import { FIELD_TYPES } from '../../constants'; // Alan tiplerini almak için

/**
 * Form Önizleme Bileşeni
 * --------------------------------------------------------------------
 * Bu bileşen, formun anlık bir görsel önizlemesini render eder.
 * Herhangi bir form gönderme veya state yönetimi mantığı içermez.
 * Sadece kendisine verilen 'form' prop'undaki veriyi ekrana çizer.
 */
const FormPreview = ({ form }) => {

  // Alanları render eden yardımcı fonksiyon
  const renderField = (field) => {
    const fieldId = `preview-${field.id}`;
    
    // Tüm alanlar için ortak, devre dışı bırakılmış proplar
    const commonProps = {
      id: fieldId,
      className: styles.formFillScreen__control,
      disabled: true, // Tüm alanlar tıklanamaz/değiştirilemez
    };

    return (
      <div key={fieldId} className={styles.formFillScreen__group}>
        <label htmlFor={fieldId} className={styles.formFillScreen__label}>
          {field.label} {field.is_required && <span style={{color: 'red'}}>*</span>}
        </label>
        
        {/* Alan tipine göre doğru HTML elementini render et */}
        {(() => {
          switch (field.field_type) {
            case FIELD_TYPES.TEXTAREA:
              return <textarea {...commonProps} />;
            
            case FIELD_TYPES.SINGLE_SELECT:
              return (
                <select {...commonProps}>
                  <option value="">Seçiniz...</option>
                  {(field.options || []).map(opt => <option key={opt.id}>{opt.label}</option>)}
                </select>
              );

            case FIELD_TYPES.MULTI_SELECT:
              return (
                <div className={styles.formFillScreen__checkboxGroup}>
                  {(field.options || []).map(opt => (
                    <div className={styles.formFillScreen__checkItem} key={opt.id}>
                      <input type="checkbox" disabled id={`${fieldId}-${opt.id}`} />
                      <label htmlFor={`${fieldId}-${opt.id}`}>{opt.label}</label>
                    </div>
                  ))}
                </div>
              );

            // Diğer tüm alan tipleri için standart bir input göster
            default:
              return <input type={field.field_type} {...commonProps} />;
          }
        })()}
      </div>
    );
  };
  
  // Eğer form veya form alanları henüz yoksa bir mesaj göster
  if (!form?.fields || form.fields.length === 0) {
    return (
      <div className={styles.formFillScreen} style={{background: 'white', padding: '2rem', textAlign: 'center'}}>
        <p>Önizleme için sol panelden bir alan ekleyin.</p>
      </div>
    );
  }

  // Ana render fonksiyonu
  return (
    <div className={styles.formFillScreen} style={{background: 'white', padding: '2rem'}}>
      {/*
        GÜNCELLEME: <form> etiketi ve 'Gönder' butonu kaldırıldı.
        Artık sadece formun görsel bir önizlemesi var.
        Sıralama işlemi, parent bileşen olan FormBuilderScreen'den gelen
        'form.fields' dizisinin sırasına göre yapılıyor.
      */}
      <div className={styles.formFillScreen__form}>
        {form.fields.map(renderField)}
      </div>
    </div>
  );
};

export default FormPreview;