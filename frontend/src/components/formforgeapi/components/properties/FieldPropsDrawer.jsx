// path: frontend/src/components/formforgeapi/components/properties/FieldPropsDrawer.jsx

import React, { useState, useEffect } from 'react';
import styles from '../../css/FieldPropsDrawer.module.css';
import { ALL_FIELD_OPTIONS, FIELDS_WITH_OPTIONS } from '../../constants';
import { useDebounce } from '../../hooks/useDebounce';

// DÜZELTME: Props listesine 'onAddOption' eklendi.
const FieldPropsDrawer = React.memo(({ field, onClose, onUpdate, onDelete, onAddOption }) => {
    // Yerel state ve debouncing mantığı, metin inputları için doğru şekilde çalışmaya devam ediyor.
    const [localField, setLocalField] = useState(field);
    const debouncedField = useDebounce(localField, 500);

    useEffect(() => {
        if (field?.id !== localField?.id) {
            setLocalField(field);
        }
    }, [field, localField?.id]);

    useEffect(() => {
        if (debouncedField && onUpdate && JSON.stringify(debouncedField) !== JSON.stringify(field)) {
            onUpdate(debouncedField);
        }
    }, [debouncedField, onUpdate, field]);


    if (!field) {
        return (
            <aside className={`${styles.drawer} ${styles.drawerPlaceholder}`}>
                <p>Özelliklerini düzenlemek için bir alan seçin.</p>
            </aside>
        );
    }

    // --- Handler Fonksiyonları ---
    const handlePropertyChange = (e) => {
        const { name, value, type, checked } = e.target;
        const newValue = type === 'checkbox' ? checked : value;
        setLocalField(prev => (prev ? { ...prev, [name]: newValue } : null));
    };

    const handleOptionChange = (newOptions) => {
        setLocalField(prev => (prev ? { ...prev, options: newOptions } : null));
    };
    
    // DÜZELTME: Bu fonksiyon artık kullanılmıyor, çünkü mantığı useFormForgeDesigner'a taşıdık.
    // const handleAddOption = () => { ... };
    
    const handleUpdateOption = (optionId, newLabel) => {
        const updatedOptions = localField.options.map(opt =>
            opt.id === optionId ? { ...opt, label: newLabel } : opt
        );
        handleOptionChange(updatedOptions);
    };
    
    const handleRemoveOption = (optionId) => {
        const updatedOptions = localField.options.filter(opt => opt.id !== optionId);
        handleOptionChange(updatedOptions);
    };

    const hasOptions = localField && FIELDS_WITH_OPTIONS.includes(localField.field_type);

    return (
        <aside className={styles.drawer}>
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
                        value={localField?.label || ''}
                        onChange={handlePropertyChange}
                    />
                </div>

                {/* Alan Tipi */}
                <div className={styles.formGroup}>
                    <label htmlFor="field_type">Alan Tipi</label>
                    <select
                        id="field_type" name="field_type"
                        className={styles.formControl}
                        value={localField?.field_type || ''}
                        onChange={handlePropertyChange}
                    >
                        {ALL_FIELD_OPTIONS.map(opt => (
                            <option key={opt.value} value={opt.value}>{opt.label}</option>
                        ))}
                    </select>
                </div>

                {/* Zorunlu Alan Checkbox */}
                <div className={styles.formGroupCheck}>
                    <input
                        type="checkbox" id="is_required" name="is_required"
                        checked={localField?.is_required || false}
                        onChange={handlePropertyChange}
                    />
                    <label htmlFor="is_required">Bu alan zorunlu</label>
                </div>
                
                {/* Seçenekler Bölümü */}
                {hasOptions && (
                    <div className={styles.formGroup}>
                        <label>Seçenekler</label>
                        <div className={styles.optionsContainer}>
                            {localField.options?.map((option, index) => (
                                <div key={option.id || index} className={styles.optionItem}>
                                    <input
                                        type="text"
                                        className={styles.formControl}
                                        placeholder={`Seçenek ${index + 1}`}
                                        value={option.label}
                                        onChange={(e) => handleUpdateOption(option.id, e.target.value)}
                                    />
                                    <button onClick={() => handleRemoveOption(option.id)} className={styles.optionButton}>&times;</button>
                                </div>
                            ))}
                        </div>
                        {/* DÜZELTME: Buton artık merkezi 'onAddOption' fonksiyonunu çağırıyor. */}
                        <button onClick={() => onAddOption(field.id)} className={styles.addButton}>
                            + Seçenek Ekle
                        </button>
                    </div>
                )}
            </div>

            <div className={styles.drawerFooter}>
                <button onClick={() => onDelete(localField.id)} className={styles.deleteButton}>
                    Alanı Sil
                </button>
            </div>
        </aside>
    );
});

export default FieldPropsDrawer;