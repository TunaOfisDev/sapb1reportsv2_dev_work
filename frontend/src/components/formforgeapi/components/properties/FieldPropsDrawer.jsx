// path: frontend/src/components/formforgeapi/components/properties/FieldPropsDrawer.jsx

import React, { useState, useEffect } from 'react';
import styles from '../../css/FieldPropsDrawer.module.css';
// DEĞİŞİKLİK: 'FIELD_TYPE_OPTIONS' yerine 'ALL_FIELD_OPTIONS' ve 'FIELDS_WITH_OPTIONS' import edildi.
import { ALL_FIELD_OPTIONS, FIELDS_WITH_OPTIONS } from '../../constants';

const FieldPropsDrawer = ({ field, onClose, onUpdate, onDelete }) => {
  // Seçili olan alanın özelliklerini düzenlemek için yerel bir state tutuyoruz.
  const [editedField, setEditedField] = useState(field);

  // Dışarıdan gelen 'field' prop'u değiştiğinde (yeni bir alan seçildiğinde)
  // yerel state'imizi güncelliyoruz.
  useEffect(() => {
    setEditedField(field);
  }, [field]);

  // Eğer hiçbir alan seçilmemişse veya state henüz oluşmamışsa,
  // sadece bir yer tutucu gösteriyoruz.
  if (!editedField) {
    return (
      <aside className={`${styles.drawer} ${styles.drawerPlaceholder}`}>
        <p>Özelliklerini düzenlemek için bir alan seçin.</p>
      </aside>
    );
  }

  // Input, select, checkbox gibi alanlardaki her değişikliği yerel state'e yazar.
  const handlePropertyChange = (e) => {
    const { name, value, type, checked } = e.target;
    const newValue = type === 'checkbox' ? checked : value;
    const updatedField = { ...editedField, [name]: newValue };
    setEditedField(updatedField);
    // Değişiklikleri anında ana state'e yansıtıyoruz.
    onUpdate(updatedField);
  };

  // --- Seçenek Yönetimi Fonksiyonları ---
  const handleAddOption = () => {
    const newOption = { id: `temp_option_${Date.now()}`, label: '', order: editedField.options.length };
    const updatedField = { ...editedField, options: [...editedField.options, newOption] };
    setEditedField(updatedField);
    onUpdate(updatedField);
  };

  const handleUpdateOption = (optionId, newLabel) => {
    const updatedOptions = editedField.options.map(opt =>
      opt.id === optionId ? { ...opt, label: newLabel } : opt
    );
    const updatedField = { ...editedField, options: updatedOptions };
    setEditedField(updatedField);
    onUpdate(updatedField);
  };

  const handleRemoveOption = (optionId) => {
    const updatedOptions = editedField.options.filter(opt => opt.id !== optionId);
    const updatedField = { ...editedField, options: updatedOptions };
    setEditedField(updatedField);
    onUpdate(updatedField);
  };
  
  // DEĞİŞİKLİK: 'options' gerektiren alanları constants'taki merkezi listeden kontrol ediyoruz.
  const hasOptions = FIELDS_WITH_OPTIONS.includes(editedField?.field_type);

  return (
    <aside className={`${styles.drawer} ${styles.drawerOpen}`}>
      <div className={styles.drawerHeader}>
        <h3 className={styles.drawerTitle}>Alan Özellikleri</h3>
        <button onClick={onClose} className={styles.drawerCloseButton}>&times;</button>
      </div>

      <div className={styles.drawerBody}>
        {/* Alan Etiketi */}
        <div className={styles.formGroup}>
          <label htmlFor="label">Etiket</label>
          <input
            type="text" id="label" name="label"
            className={styles.formControl}
            value={editedField.label}
            onChange={handlePropertyChange}
          />
        </div>

        {/* Alan Tipi */}
        <div className={styles.formGroup}>
          <label htmlFor="field_type">Alan Tipi</label>
          <select
            id="field_type" name="field_type"
            className={styles.formControl}
            value={editedField.field_type}
            onChange={handlePropertyChange}
          >
            {/* DEĞİŞİKLİK: Dropdown artık yeni ve tam listeyi kullanıyor. */}
            {ALL_FIELD_OPTIONS.map(opt => (
              <option key={opt.value} value={opt.value}>
                {opt.label}
              </option>
            ))}
          </select>
        </div>

        {/* Zorunlu Alan Checkbox */}
        <div className={styles.formGroupCheck}>
          <input
            type="checkbox" id="is_required" name="is_required"
            checked={!!editedField.is_required}
            onChange={handlePropertyChange}
          />
          <label htmlFor="is_required">Bu alan zorunlu</label>
        </div>
        
        {/* Seçenekler Bölümü (sadece ilgili alanlar için görünür) */}
        {hasOptions && (
          <div className={styles.formGroup}>
            <label>Seçenekler</label>
            <div className={styles.optionsContainer}>
              {editedField.options?.map((option, index) => (
                <div key={option.id || index} className={styles.optionItem}>
                  <input
                    type="text"
                    className={styles.formControl}
                    placeholder={`Seçenek ${index + 1}`}
                    value={option.label}
                    onChange={(e) => handleUpdateOption(option.id, e.target.value)}
                  />
                  <button onClick={() => handleRemoveOption(option.id)} className={styles.optionButton}>
                    &times;
                  </button>
                </div>
              ))}
            </div>
            <button onClick={handleAddOption} className={styles.addButton}>
              + Seçenek Ekle
            </button>
          </div>
        )}
      </div>

      <div className={styles.drawerFooter}>
        <button onClick={() => onDelete(editedField.id)} className={styles.deleteButton}>
          Alanı Sil
        </button>
      </div>
    </aside>
  );
};

export default FieldPropsDrawer;