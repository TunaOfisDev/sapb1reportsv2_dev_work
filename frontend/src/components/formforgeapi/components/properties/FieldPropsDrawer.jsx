// path: frontend/src/components/formforgeapi/components/properties/FieldPropsDrawer.jsx

import React, { useState, useEffect } from 'react';
import styles from '../../css/FieldPropsDrawer.module.css';
import { ALL_FIELD_OPTIONS, FIELDS_WITH_OPTIONS } from '../../constants';
import { useDebounce } from '../../hooks/useDebounce';

const FieldPropsDrawer = React.memo(({ field, onClose, onUpdate, onDelete, onAddOption }) => {
    const [localField, setLocalField] = useState(field);
    const debouncedField = useDebounce(localField, 500);

    const [newOption, setNewOption] = useState({ label: '', value: '' });
    const [isAdding, setIsAdding] = useState(false);
    const [addError, setAddError] = useState(null);

    useEffect(() => {
    // Sadece objelerin içeriği gerçekten değiştiyse state'i güncelle
    if (JSON.stringify(field) !== JSON.stringify(localField)) {
         setLocalField(field);
    }
    }, [field]);

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

    const handlePropertyChange = (e) => {
        const { name, value, type, checked } = e.target;
        const newValue = type === 'checkbox' ? checked : value;
        setLocalField(prev => (prev ? { ...prev, [name]: newValue } : null));
    };

    const handleAddNewOptionClick = async () => {
        if (isAdding || !newOption.label.trim()) return;

        setIsAdding(true);
        setAddError(null);
        try {
            await onAddOption(newOption);
            
            // DİKKAT: Bu satır, seri ekleme yapabilmeniz için kasıtlı olarak
            // yorum satırı haline getirilmiştir. Input'u temizlemez.
            // setNewOption({ label: '', value: '' }); 

        } catch (error) {
            setAddError(error.message || "Bir hata oluştu.");
        } finally {
            setIsAdding(false);
        }
    };
    
    const handleOptionChange = (newOptions) => {
        setLocalField(prev => (prev ? { ...prev, options: newOptions } : null));
    };
    
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
                        <div className={styles.addOptionForm}>
                            <input
                                type="text"
                                className={styles.formControl}
                                placeholder="Yeni Seçenek Etiketi"
                                value={newOption.label}
                                onChange={(e) => {
                                    setNewOption({ ...newOption, label: e.target.value });
                                    setAddError(null);
                                }}
                            />
                            <button onClick={handleAddNewOptionClick} className={styles.addButton} disabled={isAdding || !newOption.label.trim()}>
                                {isAdding ? 'Ekleniyor...' : '+ Seçenek Ekle'}
                            </button>
                        </div>
                        {addError && <p className={styles.errorMessage}>{addError}</p>}
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