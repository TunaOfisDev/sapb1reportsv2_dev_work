// path: frontend/src/components/formforgeapi/components/properties/FieldPropsDrawer.jsx

import React, { useState, useEffect } from 'react';
import styles from '../../css/FieldPropsDrawer.module.css';
import { ALL_FIELD_OPTIONS, FIELDS_WITH_OPTIONS } from '../../constants';
import { useDebounce } from '../../hooks/useDebounce'; // Debounce hook'unuzun doğru yolda olduğundan emin olun.

// Bileşeni `React.memo` ile sarmak, gereksiz render'lara karşı ek bir koruma katmanıdır.
const FieldPropsDrawer = React.memo(({ field, onClose, onUpdate, onDelete }) => {
    // 1. YEREL STATE: Input değişikliklerini anında yakalamak için bileşenin kendi state'i.
    const [localField, setLocalField] = useState(field);
    
    // 2. DEBOUNCE: API'ye sürekli istek atmamak için yerel state'i gecikmeli takip et.
    const debouncedField = useDebounce(localField, 500);

    // --- İŞTE KESİN ÇÖZÜM BURADA ---
    useEffect(() => {
        // Bu effect, dışarıdan gelen `field` prop'unu dinler.
        // ANCAK, sadece seçilen alanın ID'si değiştiğinde (yani kullanıcı FARKLI bir alana tıkladığında)
        // yerel state'i sıfırlar. Bu, siz aynı alanda yazarken verinizin ezilmesini ENGELLER.
        if (field?.id !== localField?.id) {
            setLocalField(field);
        }
    }, [field, localField?.id]); // Bağımlılık dizisi bu kontrolü sağlar.

    // 3. API'Yİ GÜNCELLEME: Sadece kullanıcı yazmayı bıraktığında çalışır.
    useEffect(() => {
        // `debouncedField` değiştiğinde ve bu bir güncelleme ise `onUpdate`'i çağır.
        if (debouncedField && onUpdate && JSON.stringify(debouncedField) !== JSON.stringify(field)) {
            onUpdate(debouncedField);
        }
    }, [debouncedField, onUpdate, field]);


    // Eğer bir alan seçilmemişse, yer tutucu gösterilir.
    if (!field) { // Dışarıdan gelen `field` prop'una göre boş durum kontrolü yapılır.
        return (
            <aside className={`${styles.drawer} ${styles.drawerPlaceholder}`}>
                <p>Özelliklerini düzenlemek için bir alan seçin.</p>
            </aside>
        );
    }

    // --- Handler Fonksiyonları ---
    // Bu fonksiyon sadece yerel state'i günceller, çok hızlı çalışır.
    const handlePropertyChange = (e) => {
        const { name, value, type, checked } = e.target;
        const newValue = type === 'checkbox' ? checked : value;
        setLocalField(prev => (prev ? { ...prev, [name]: newValue } : null));
    };

    const handleOptionChange = (newOptions) => {
        setLocalField(prev => (prev ? { ...prev, options: newOptions } : null));
    };

    const handleAddOption = () => {
        const currentOptions = localField?.options || [];
        const newOption = { id: `temp_option_${Date.now()}`, label: '', order: currentOptions.length };
        handleOptionChange([...currentOptions, newOption]);
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
                {/* Input'lar artık `localField` state'ine bağlıdır. */}
                <div className={styles.formGroup}>
                    <label htmlFor="label">Etiket</label>
                    <input
                        type="text" id="label" name="label"
                        className={styles.formControl}
                        value={localField?.label || ''}
                        onChange={handlePropertyChange}
                    />
                </div>

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

                <div className={styles.formGroupCheck}>
                    <input
                        type="checkbox" id="is_required" name="is_required"
                        checked={localField?.is_required || false}
                        onChange={handlePropertyChange}
                    />
                    <label htmlFor="is_required">Bu alan zorunlu</label>
                </div>
                
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
                        <button onClick={handleAddOption} className={styles.addButton}>+ Seçenek Ekle</button>
                    </div>
                )}
            </div>

            <div className={styles.drawerFooter}>
                <button onClick={() => onDelete(localField.id)} className={styles.deleteButton}>Alanı Sil</button>
            </div>
        </aside>
    );
});

export default FieldPropsDrawer;