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
                title: "Form Fields",
                rows: [{ id: `row-${form.id}-1`, fields: sortedFields }],
            }]);
        } else {
            setLayout([]);
        }
    }, [form]);

    const selectedField = useMemo(() => {
        if (!selectedFieldId || !layout) return null;
        for (const section of layout) {
            for (const row of section.rows) {
                const field = row.fields.find(f => f.id === selectedFieldId);
                if (field) return field;
            }
        }
        return null;
    }, [selectedFieldId, layout]);

    const handleSelectField = useCallback((fieldId) => {
        setSelectedFieldId(prevId => (prevId === fieldId ? null : fieldId));
    }, []);

    // YENİ: Alan seçimini kapatmak (drawer'ı kapatmak) için referansı sabit bir fonksiyon.
    // Bu, FormBuilderScreen'de inline fonksiyon kullanımını engeller ve React.memo'nun doğru çalışmasını sağlar.
    const handleCloseDrawer = useCallback(() => {
        setSelectedFieldId(null);
    }, []);

    const handleUpdateField = useCallback(async (fieldData) => {
        setLayout(prevLayout =>
            prevLayout.map(section => ({
                ...section,
                rows: section.rows.map(row => ({
                    ...row,
                    fields: row.fields.map(f => f.id === fieldData.id ? fieldData : f),
                })),
            }))
        );

        if (String(fieldData.id).includes('temp_')) return;
        try {
            await FormForgeApiApi.updateFormField(fieldData.id, fieldData);
        } catch (error) {
            console.error("An error occurred while updating the field.", error);
            onFormUpdate(form.id);
        }
    }, [form?.id, onFormUpdate]);

    const handleAddOption = useCallback(async (optionData) => {
        if (!selectedField) {
            console.error("No field selected to add an option to.");
            return;
        }

        if (!optionData || !optionData.label || optionData.label.trim() === '') {
            console.error("Option label cannot be empty.");
            throw new Error("Seçenek etiketi boş olamaz.");
        }

        const currentOptions = selectedField.options || [];
        
        const payload = {
            label: optionData.label.trim(),
            value: (optionData.value || '').trim() || optionData.label.trim(),
            order: currentOptions.length,
        };

        try {
            const response = await FormForgeApiApi.addFormFieldOption(selectedField.id, payload);
            const newOptionFromServer = response.data;

            setLayout(prevLayout =>
                prevLayout.map(section => ({
                    ...section,
                    rows: section.rows.map(row => ({
                        ...row,
                        fields: row.fields.map(field => {
                            if (field.id === selectedField.id) {
                                return {
                                    ...field,
                                    options: [...(field.options || []), newOptionFromServer]
                                };
                            }
                            return field;
                        })
                    }))
                }))
            );
        } catch (error) {
            console.error("API error while adding a new option:", error);
            throw error;
        }
    }, [selectedField]);

    const handleDeleteField = useCallback(async (fieldId) => {
        if (!form?.id || !fieldId || !window.confirm("Bu alanı silmek istediğinizden emin misiniz?")) return;

        setLayout(prevLayout =>
            prevLayout.map(section => ({
                ...section,
                rows: section.rows.map(row => ({
                    ...row,
                    fields: row.fields.filter(f => f.id !== fieldId),
                })),
            }))
        );
        // Drawer'ı kapatmak için yeni fonksiyonu burada da kullanabiliriz.
        handleCloseDrawer();

        try {
            await FormForgeApiApi.deleteFormField(fieldId);
            await onFormUpdate(form.id);
        } catch (error) {
            console.error("An error occurred while deleting the field.", error);
            onFormUpdate(form.id);
        }
    }, [form?.id, onFormUpdate, handleCloseDrawer]);
    
    const handleDragEnd = useCallback(async (event) => {
        const { active, over } = event;
        if (!over) return;
    
        let finalLayout = [];
        setLayout(currentLayout => {
            let newLayout = JSON.parse(JSON.stringify(currentLayout));
            const findContainer = (id) => newLayout.flatMap(s => s.rows).find(r => r.id === id || r.fields.some(f => f.id === id));
            const overContainer = findContainer(over.id);
            if (!overContainer) return currentLayout;

            if (active.data.current?.isPaletteItem) {
                const newField = { ...createEmptyField({ type: active.data.current.fieldType }), form: form.id, id: `temp_${uuidv4()}` };
                const overIndex = over.id === overContainer.id ? overContainer.fields.length : overContainer.fields.findIndex(f => f.id === over.id);
                overContainer.fields.splice(overIndex, 0, newField);
            } else {
                const activeContainer = findContainer(active.id);
                if (!activeContainer || active.id === over.id) return currentLayout;
                
                const activeIndex = activeContainer.fields.findIndex(f => f.id === active.id);
                const [movedField] = activeContainer.fields.splice(activeIndex, 1);
                const overIndex = over.id === overContainer.id ? overContainer.fields.length : overContainer.fields.findIndex(f => f.id === over.id);
                overContainer.fields.splice(overIndex >= 0 ? overIndex : overContainer.fields.length, 0, movedField);
            }
            finalLayout = newLayout;
            return newLayout;
        });

        try {
            const allFields = finalLayout.flatMap(s => s.rows.flatMap(r => r.fields));
            const payload = allFields.map((field, index) => ({ ...field, order: index }));
            const newFieldPayload = payload.find(f => String(f.id).includes('temp_'));
            
            if (newFieldPayload) {
                const { id, ...apiData } = newFieldPayload;
                await FormForgeApiApi.createFormField(apiData);
                await onFormUpdate(form.id);
            } else {
                const orderPayload = payload.map(({ id, order }) => ({ id, order }));
                await FormForgeApiApi.updateFormFieldOrder(orderPayload);
            }
        } catch (error) {
            console.error("Error after drag-and-drop:", error);
            onFormUpdate(form.id);
        }
    }, [form, onFormUpdate]);

    const handleAddRow = useCallback((sectionId) => {
        setLayout(prevLayout =>
            prevLayout.map(section => {
                if (section.id === sectionId) {
                    return { ...section, rows: [...section.rows, { id: `row_${uuidv4()}`, fields: [] }] };
                }
                return section;
            })
        );
    }, []);

    // Dışarıya aktarılan fonksiyonlar listesine handleCloseDrawer eklendi.
    return {
        layout,
        selectedFieldId,
        viewMode,
        setViewMode,
        selectedField,
        onDragEnd: handleDragEnd,
        handleSelectField,
        handleUpdateField,
        handleDeleteField,
        handleAddRow,
        handleAddOption,
        handleCloseDrawer, // YENİ
    };
}