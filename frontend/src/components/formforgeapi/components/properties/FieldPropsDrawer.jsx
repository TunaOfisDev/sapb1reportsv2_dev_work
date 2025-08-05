// path: frontend/src/components/formforgeapi/components/properties/FieldPropsDrawer.jsx

import React, { useState, useEffect } from 'react'; // useState ve useEffect eklendi
import styles from '../../css/FieldPropsDrawer.module.css';
import FieldProperty from './FieldProperty';
import { FIELD_TYPE_OPTIONS } from '../../constants';
import { addOption, updateOption, removeOption } from '../../utils/optionUtils';

const FieldPropsDrawer = ({ field, onClose, onUpdate, onDelete }) => {
  // YENİ: Bileşen içinde düzenlenmekte olan alan için geçici bir state tutuyoruz.
  const [editedField, setEditedField] = useState(field);

  // Prop olarak gelen 'field' değiştiğinde (yeni bir alan seçildiğinde),
  // iç state'imizi güncelliyoruz.
  useEffect(() => {
    setEditedField(field);
  }, [field]);

  // Eğer hiçbir alan seçilmemişse veya state henüz oluşmamışsa, paneli render etme.
  if (!editedField) {
    return null;
  }

  // DEĞİŞTİ: Bu fonksiyon artık doğrudan ana state'i değil, yerel 'editedField' state'ini güncelliyor.
  const handlePropertyChange = (propName, value) => {
    setEditedField(prev => ({ ...prev, [propName]: value }));
  };

  const handleOptionChange = (newOptions) => {
    setEditedField(prev => ({ ...prev, options: newOptions }));
  };
  
  const handleAddOptionClick = () => {
    const newFieldState = addOption(editedField);
    handleOptionChange(newFieldState.options);
  };

  const handleUpdateOptionClick = (optionId, newLabel) => {
    const newFieldState = updateOption(editedField, optionId, newLabel);
    handleOptionChange(newFieldState.options);
  };

  const handleRemoveOptionClick = (optionId) => {
    const newFieldState = removeOption(editedField, optionId);
    handleOptionChange(newFieldState.options);
  };

  const handleDeleteFieldClick = () => {
    onDelete(editedField.id);
  };

  // YENİ: Kaydet butonu için fonksiyon. Değişiklikleri ana hook'a bu fonksiyon gönderir.
  const handleSaveChanges = () => {
    onUpdate(editedField);
  };
  
  const hasOptions = ['singleselect', 'multiselect', 'radio'].includes(editedField?.field_type);

  return (
    <>
      <div className={`${styles.fieldPropsDrawer} ${styles['fieldPropsDrawer--open']}`}>
        <div className={styles.fieldPropsDrawer__header}>
          <h3 className={styles.fieldPropsDrawer__title}>Alan Özellikleri</h3>
          <button onClick={onClose} className={styles.fieldPropsDrawer__close}>&times;</button>
        </div>

        <div className={styles.fieldPropsDrawer__body}>
          <FieldProperty label="Alan Etiketi" htmlFor={`prop-label-${editedField.id}`}>
            {/* DEĞİŞTİ: Değerler artık 'editedField' state'inden geliyor */}
            <input
              id={`prop-label-${editedField.id}`}
              type="text"
              className={styles.fieldPropsDrawer__control}
              value={editedField.label}
              onChange={(e) => handlePropertyChange('label', e.target.value)}
            />
          </FieldProperty>

          <FieldProperty label="Alan Tipi" htmlFor={`prop-type-${editedField.id}`}>
            <select
              id={`prop-type-${editedField.id}`}
              className={styles.fieldPropsDrawer__control}
              value={editedField.field_type}
              onChange={(e) => handlePropertyChange('field_type', e.target.value)}
            >
              {FIELD_TYPE_OPTIONS.map(opt => (
                <option key={opt.value} value={opt.value}>{opt.label}</option>
              ))}
            </select>
          </FieldProperty>

          <div className={styles.fieldPropsDrawer__group}>
            <label className={styles.fieldPropsDrawer__inlineLabel}>
              <input
                type="checkbox"
                checked={editedField.is_required}
                onChange={(e) => handlePropertyChange('is_required', e.target.checked)}
              />
              Zorunlu Alan
            </label>
          </div>

          {hasOptions && (
            <div className={styles.fieldPropsDrawer__group}>
              <label className={styles.fieldPropsDrawer__label}>Seçenekler</label>
              {editedField.options.map((option, index) => (
                <div key={option.id} style={{ display: 'flex', gap: '0.5rem', marginBottom: '0.25rem' }}>
                  <input
                    type="text"
                    className={styles.fieldPropsDrawer__control}
                    placeholder={`Seçenek ${index + 1}`}
                    value={option.label}
                    onChange={(e) => handleUpdateOptionClick(option.id, e.target.value)}
                  />
                  <button onClick={() => handleRemoveOptionClick(option.id)} title="Seçeneği Sil" className={styles.fieldPropsDrawer__btnSecondary}>
                    &times;
                  </button>
                </div>
              ))}
              <button onClick={handleAddOptionClick} className={styles.fieldPropsDrawer__btn}>
                + Seçenek Ekle
              </button>
            </div>
          )}
        </div>

        <div className={styles.fieldPropsDrawer__footer}>
          <button onClick={handleDeleteFieldClick} className={styles.fieldPropsDrawer__btnSecondary} style={{color: '#d92d20', marginRight: 'auto'}}>
            Alanı Sil
          </button>
          {/* YENİ: KAYDET BUTONU */}
          <button onClick={handleSaveChanges} className={styles.fieldPropsDrawer__btnPrimary}>
            Değişiklikleri Kaydet
          </button>
        </div>
      </div>
      <div
        className={`${styles.fieldPropsDrawer__backdrop} ${styles['fieldPropsDrawer--open']}`}
        onClick={onClose}
      />
    </>
  );
};

export default FieldPropsDrawer;