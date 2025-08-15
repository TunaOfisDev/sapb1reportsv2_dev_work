// path: frontend/src/components/formforgeapi/components/properties/FieldPropsDrawer.jsx

import React, { useState, useEffect, useMemo } from 'react';
import styles from '../../css/FieldPropsDrawer.module.css';
import { ALL_FIELD_OPTIONS, FIELDS_WITH_OPTIONS } from '../../constants';
import { useDebounce } from '../../hooks/useDebounce';

const FieldPropsDrawer = React.memo(({ field, onClose, onUpdate, onDelete, onAddOption }) => {
    const [localField, setLocalField] = useState(field);
    
    const fieldPropertiesToUpdate = useMemo(() => {
        if (!localField) return null;
        const { options, ...properties } = localField;
        return properties;
    }, [localField]);

    const debouncedFieldProperties = useDebounce(fieldPropertiesToUpdate, 500);

    const [newOption, setNewOption] = useState({ label: '', value: '' });
    const [isAdding, setIsAdding] = useState(false);
    const [addError, setAddError] = useState(null);

    useEffect(() => {
        if (JSON.stringify(field) !== JSON.stringify(localField)) {
            setLocalField(field);
        }
    }, [field]);

    // Bu useEffect artık SADECE label, is_required gibi temel özellikleri günceller.
    useEffect(() => {
        if (debouncedFieldProperties && onUpdate) {
            const { options, ...originalProperties } = field || {};
            if (JSON.stringify(debouncedFieldProperties) !== JSON.stringify(originalProperties)) {
                // ÖNEMLİ: Güncelleme yaparken, 'options' dizisinin en güncel halini 'field' prop'undan alıyoruz.
                // Bu, seçeneklerin üzerine yanlışlıkla eski veriyle yazılmasını engeller.
                onUpdate({ ...debouncedFieldProperties, options: field?.options || [] });
            }
        }
    }, [debouncedFieldProperties, onUpdate, field]);

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
            // onAddOption, hook'ta API'ye gider ve layout'u günceller.
            await onAddOption(newOption); 
            setNewOption({ label: '', value: '' });
        } catch (error) {
            setAddError(error.message || "Bir hata oluştu.");
        } finally {
            setIsAdding(false);
        }
    };
    
    // ==============================================================================
    // ===                           ANA DÜZELTME BURADA                          ===
    // ==============================================================================

    const handleUpdateOption = (optionId, newLabel) => {
        // 1. Yeni 'options' dizisini immutable olarak oluştur.
        const updatedOptions = localField.options.map(opt =>
            opt.id === optionId ? { ...opt, label: newLabel } : opt
        );
        
        // 2. Güncellenmiş alanın tamamını oluştur.
        const updatedField = { ...localField, options: updatedOptions };

        // 3. Hem local state'i hem de DEBOUNCE OLMADAN doğrudan parent'ı (hook'u) anında güncelle.
        setLocalField(updatedField);
        onUpdate(updatedField); 
    };
    
    const handleRemoveOption = (optionId) => {
        // 1. Yeni 'options' dizisini immutable olarak oluştur.
        const updatedOptions = localField.options.filter(opt => opt.id !== optionId);
        
        // 2. Güncellenmiş alanın tamamını oluştur.
        const updatedField = { ...localField, options: updatedOptions };

        // 3. Hem local state'i hem de DEBOUNCE OLMADAN doğrudan parent'ı (hook'u) anında güncelle.
        setLocalField(updatedField);
        onUpdate(updatedField);
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