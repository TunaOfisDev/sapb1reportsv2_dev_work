// path: frontend/src/components/formforgeapi/components/properties/FieldPropsDrawer.jsx

import React, { useState, useEffect } from 'react';
import styles from '../../css/FieldPropsDrawer.module.css';
import { ALL_FIELD_OPTIONS, FIELDS_WITH_OPTIONS } from '../../constants';
import { useDebounce } from '../../hooks/useDebounce'; // YENİ: Debounce hook'unu import et

const FieldPropsDrawer = ({ field, onClose, onUpdate, onDelete }) => {
  const [editedField, setEditedField] = useState(field);
  
  // YENİ: editedField state'ini 500ms gecikmeyle takip eden debounced bir değer oluştur.
  const debouncedField = useDebounce(editedField, 500);

  useEffect(() => {
    setEditedField(field);
  }, [field]);

  // YENİ: Bu effect, SADECE kullanıcı yazmayı bıraktıktan sonra çalışır.
  useEffect(() => {
    // `debouncedField` değiştiğinde ve `onUpdate` prop'u mevcutsa,
    // ve bu eski bir field değilse, değişikliği ana hook'a gönder.
    if (debouncedField && onUpdate && debouncedField.id === field?.id) {
      onUpdate(debouncedField);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [debouncedField, onUpdate]); // Sadece debouncedField veya onUpdate değiştiğinde çalışır


  if (!editedField) {
    return (
      <aside className={`${styles.drawer} ${styles.drawerPlaceholder}`}>
        <p>Özelliklerini düzenlemek için bir alan seçin.</p>
      </aside>
    );
  }

  // GÜNCELLEME: Bu fonksiyon artık SADECE yerel state'i güncelliyor. API isteğini tetiklemiyor.
  const handlePropertyChange = (e) => {
    const { name, value, type, checked } = e.target;
    const newValue = type === 'checkbox' ? checked : value;
    setEditedField(prev => ({ ...prev, [name]: newValue }));
  };

  const handleOptionChange = (newOptions) => {
    setEditedField(prev => ({ ...prev, options: newOptions }));
  };

  // ... (Diğer handle fonksiyonları da sadece setEditedField kullanacak şekilde kalabilir)
  const handleAddOption = () => {
    const newOption = { id: `temp_option_${Date.now()}`, label: '', order: editedField.options.length };
    handleOptionChange([...editedField.options, newOption]);
  };
  const handleUpdateOption = (optionId, newLabel) => {
    const updatedOptions = editedField.options.map(opt =>
      opt.id === optionId ? { ...opt, label: newLabel } : opt
    );
    handleOptionChange(updatedOptions);
  };
  const handleRemoveOption = (optionId) => {
    const updatedOptions = editedField.options.filter(opt => opt.id !== optionId);
    handleOptionChange(updatedOptions);
  };

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
            value={editedField.label || ''} // Kontrolsüz bileşenden kontrollüye geçiş hatasını önle
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
        
        {/* Seçenekler Bölümü */}
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