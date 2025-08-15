// path: frontend/src/components/formforgeapi/hooks/useFormForgeDesigner.js

import { useState, useEffect, useMemo, useCallback } from "react";
import FormForgeApiApi from "../api/FormForgeApiApi";
import { createEmptyField } from "../constants";
import { v4 as uuidv4 } from 'uuid';

export default function useFormForgeDesigner(form, onFormUpdate) {
    const [layout, setLayout] = useState([]);
    const [selectedFieldId, setSelectedFieldId] = useState(null);
    const [viewMode, setViewMode] = useState("design");

    useEffect(() => {
        if (form?.fields) {
            const sortedFields = [...form.fields].sort((a, b) => a.order - b.order);
            setLayout([{
                id: `section-${form.id}`,
                title: "Form Alanları",
                rows: [{ id: `row-${form.id}-1`, fields: sortedFields }],
            }]);
        } else {
            setLayout([]);
        }
    }, [form]);

    const selectedField = useMemo(() => {
        if (!selectedFieldId || !layout) return null;
        return layout.flatMap(s => s.rows.flatMap(r => r.fields)).find(f => f.id === selectedFieldId);
    }, [selectedFieldId, layout]);

    const handleSelectField = useCallback((fieldId) => {
        setSelectedFieldId(prevId => (prevId === fieldId ? null : fieldId));
    }, []);

    const handleCloseDrawer = useCallback(() => {
        setSelectedFieldId(null);
    }, []);
    
    const updateFieldInLayout = useCallback((fieldId, updaterFn) => {
        setLayout(prevLayout =>
            prevLayout.map(section => ({
                ...section,
                rows: section.rows.map(row => ({
                    ...row,
                    fields: row.fields.map(field => 
                        field.id === fieldId ? updaterFn(field) : field
                    ),
                })),
            }))
        );
    }, []);

    // ==============================================================================
    // ===                           ANA DÜZELTME BURADA                          ===
    // ==============================================================================
    const handleUpdateField = useCallback(async (updatedData) => {
        let fullFieldToSave;

        // Arayüzü anında güncelle. Gelen veriyi mevcut state ile birleştirerek
        // 'options' dizisinin kaybolmamasını garanti altına alıyoruz.
        updateFieldInLayout(updatedData.id, (currentField) => {
            fullFieldToSave = { ...currentField, ...updatedData };
            return fullFieldToSave;
        });

        // Eğer state güncellemesi hemen gerçekleşmezse diye, API'ye gönderilecek veriyi
        // bir önceki adımda oluşturduğumuz `fullFieldToSave` değişkeninden alıyoruz.
        if (String(updatedData.id).startsWith('temp_')) return;
        
        try {
            // API'ye her zaman alanın tam ve en güncel halini gönderiyoruz.
            await FormForgeApiApi.updateFormField(updatedData.id, fullFieldToSave);
        } catch (error) {
            console.error("Alan güncellenirken hata oluştu:", error);
            onFormUpdate(form.id); 
        }
    }, [form?.id, onFormUpdate, updateFieldInLayout]);

    const handleAddOption = useCallback(async (optionData) => {
        const currentSelectedField = layout.flatMap(s => s.rows.flatMap(r => r.fields)).find(f => f.id === selectedFieldId);
        if (!currentSelectedField) return;
        if (!optionData?.label?.trim()) throw new Error("Seçenek etiketi boş olamaz.");

        const payload = {
            label: optionData.label.trim(),
            value: (optionData.value || '').trim() || optionData.label.trim(),
            order: currentSelectedField.options?.length || 0,
        };

        try {
            const response = await FormForgeApiApi.addFormFieldOption(currentSelectedField.id, payload);
            const newOptionFromServer = response.data;
            
            updateFieldInLayout(currentSelectedField.id, (field) => ({
                ...field,
                options: [...(field.options || []), newOptionFromServer],
            }));
        } catch (error) {
            console.error("Seçenek eklenirken API hatası:", error);
            throw error;
        }
    }, [layout, selectedFieldId, updateFieldInLayout]);

    const handleDeleteField = useCallback(async (fieldId) => {
        if (!window.confirm("Bu alanı silmek istediğinizden emin misiniz?")) return;
        
        setLayout(prevLayout =>
            prevLayout.map(section => ({
                ...section,
                rows: section.rows.map(row => ({
                    ...row,
                    fields: row.fields.filter(f => f.id !== fieldId),
                })),
            }))
        );
        handleCloseDrawer();

        try {
            await FormForgeApiApi.deleteFormField(fieldId);
        } catch (error) {
            console.error("Alan silinirken hata oluştu:", error);
            onFormUpdate(form.id);
        }
    }, [form?.id, onFormUpdate, handleCloseDrawer]);

    const handleDragEnd = useCallback(async (event) => {
        const { active, over } = event;
        if (!over) return;
    
        let nextLayout = layout; 
    
        setLayout(currentLayout => {
            const newLayout = JSON.parse(JSON.stringify(currentLayout));
            const allRows = newLayout.flatMap(s => s.rows);
            const findRow = (itemId) => allRows.find(r => r.id === itemId || r.fields.some(f => f.id === itemId));
            const activeRow = findRow(active.id);
            const overRow = findRow(over.id);
    
            if (!activeRow || !overRow) return currentLayout;
    
            if (active.data.current?.isPaletteItem) {
                const newField = { 
                    ...createEmptyField({ type: active.data.current.fieldType }), 
                    form: form.id, 
                    id: `temp_${uuidv4()}` 
                };
                const overIndex = over.id === overRow.id ? overRow.fields.length : overRow.fields.findIndex(f => f.id === over.id);
                overRow.fields.splice(overIndex, 0, newField);
            } else {
                if (active.id === over.id) return currentLayout;
    
                const activeIndex = activeRow.fields.findIndex(f => f.id === active.id);
                const [movedField] = activeRow.fields.splice(activeIndex, 1);
                const overIndex = over.id === overRow.id ? overRow.fields.length : overRow.fields.findIndex(f => f.id === over.id);
                overRow.fields.splice(overIndex, 0, movedField);
            }
            nextLayout = newLayout;
            return nextLayout;
        });
    
        try {
            const allFields = nextLayout.flatMap(s => s.rows.flatMap(r => r.fields));
            const newField = allFields.find(f => String(f.id).startsWith('temp_'));
    
            if (newField) {
                const { id, ...apiData } = newField;
                const payload = {...apiData, order: allFields.findIndex(f => f.id === newField.id)};
                await FormForgeApiApi.createFormField(payload);
                await onFormUpdate(form.id);
            } else {
                const orderPayload = allFields.map(({ id }, index) => ({ id, order: index }));
                await FormForgeApiApi.updateFormFieldOrder(orderPayload);
            }
        } catch (error) {
            console.error("Sürükle-bırak sonrası hata:", error);
            onFormUpdate(form.id);
        }
    }, [form, layout, onFormUpdate]);

    return {
        layout,
        selectedField,
        viewMode,
        setViewMode,
        onDragEnd: handleDragEnd,
        handleSelectField,
        handleCloseDrawer,
        actions: {
            onUpdateField: handleUpdateField,
            onDeleteField: handleDeleteField,
            onAddOption: handleAddOption, 
        }
    };
}