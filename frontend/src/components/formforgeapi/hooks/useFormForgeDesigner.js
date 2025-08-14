// path: frontend/src/components/formforgeapi/hooks/useFormForgeDesigner.js

import { useState, useEffect, useMemo, useCallback } from "react";
import FormForgeApiApi from "../api/FormForgeApiApi";
import { createEmptyField } from "../constants";
import { v4 as uuidv4 } from 'uuid';

/**
 * The central hook that manages all UI logic and state for the FormForge Designer.
 * @param {object} form - The form object fetched from the backend.
 * @param {function} onFormUpdate - A callback function to re-fetch the main form,
 * used when a new field is created or a critical error occurs.
 */
export default function useFormForgeDesigner(form, onFormUpdate) {
    // --- STATE DEFINITIONS ---
    const [layout, setLayout] = useState([]); // Holds the visual layout of the form (sections, rows, fields)
    const [selectedFieldId, setSelectedFieldId] = useState(null); // The ID of the field selected for editing
    const [viewMode, setViewMode] = useState("design"); // 'design' | 'preview'

    // --- EFFECTS ---
    // Rebuilds the layout when the 'form' prop from outside changes.
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
    }, [form]); // Only triggers when the main form object changes.

    // --- MEMOIZED VALUES ---
    // Gets the selected field object without recalculating on every render.
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

    // --- CALLBACK FUNCTIONS ---

    // Sets the selected field when a field card is clicked.
    const handleSelectField = useCallback((fieldId) => {
        setSelectedFieldId(prevId => (prevId === fieldId ? null : fieldId));
    }, []);

    // Updates a field's properties.
    const handleUpdateField = useCallback(async (fieldData) => {
        // Optimistically update the UI instantly with the new data.
        setLayout(prevLayout =>
            prevLayout.map(section => ({
                ...section,
                rows: section.rows.map(row => ({
                    ...row,
                    fields: row.fields.map(f => f.id === fieldData.id ? fieldData : f),
                })),
            }))
        );

        // Call the API in the background to persist the change.
        if (String(fieldData.id).includes('temp_')) return; // Don't save temporary fields
        try {
            await FormForgeApiApi.updateFormField(fieldData.id, fieldData);
            // On success, we DON'T need to re-fetch the form. Our local state is the source of truth.
        } catch (error) {
            console.error("An error occurred while updating the field.", error);
            // If there's an error, re-fetch the form from the server to ensure data consistency.
            onFormUpdate(form.id); 
        }
    }, [form?.id, onFormUpdate]);

    // **NEW AND CORRECTED FUNCTION FOR ADDING AN OPTION**
    const handleAddOption = useCallback(async (fieldId) => {
        const newOptionPayload = { label: '', value: '' }; // Clean data to send to the API

        try {
            // 1. Call the new, dedicated 'add-option' API endpoint.
            const response = await FormForgeApiApi.addFormFieldOption(fieldId, newOptionPayload);
            const newOptionFromServer = response.data; // The new option with its real ID from the backend

            // 2. On success, update the UI with the confirmed data from the backend.
            setLayout(prevLayout =>
                prevLayout.map(section => ({
                    ...section,
                    rows: section.rows.map(row => ({
                        ...row,
                        fields: row.fields.map(field => {
                            if (field.id === fieldId) {
                                const currentOptions = field.options || [];
                                // Add the new, real option to the list of existing options
                                return {
                                    ...field,
                                    options: [...currentOptions, newOptionFromServer]
                                };
                            }
                            return field;
                        })
                    }))
                }))
            );
        } catch (error) {
            console.error("API error while adding a new option:", error);
            // A user notification (toast) could be shown here.
        }
    }, []); // This function has no external dependencies.

    // Deletes a field.
    const handleDeleteField = useCallback(async (fieldId) => {
        if (!form?.id || !fieldId || !window.confirm("Are you sure you want to delete this field?")) return;
        
        setLayout(prevLayout =>
            prevLayout.map(section => ({
                ...section,
                rows: section.rows.map(row => ({
                    ...row,
                    fields: row.fields.filter(f => f.id !== fieldId),
                })),
            }))
        );
        setSelectedFieldId(null);

        try {
            await FormForgeApiApi.deleteFormField(fieldId);
            await onFormUpdate(form.id); // Re-fetching after delete ensures order is correct.
        } catch (error) {
            console.error("An error occurred while deleting the field.", error);
            onFormUpdate(form.id);
        }
    }, [form?.id, onFormUpdate]);

    // Handles the drag-and-drop operation.
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
                await onFormUpdate(form.id); // Re-fetch to get the new ID.
            } else {
                const orderPayload = payload.map(({ id, order }) => ({ id, order }));
                await FormForgeApiApi.updateFormFieldOrder(orderPayload);
                // No need to re-fetch after sorting, the UI is already correct.
            }
        } catch (error) {
            console.error("Error after drag-and-drop:", error);
            onFormUpdate(form.id); // Revert to the last known good state from the server on error.
        }
    }, [form, onFormUpdate]);

    // Adds a new row.
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

    // --- HOOK'S PUBLIC INTERFACE ---
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
        handleAddOption, // The corrected function
    };
}