// path: frontend/src/components/formforgeapi/hooks/useFormForgeDesigner.js

import { useState, useEffect, useMemo, useCallback } from "react";
import { arrayMove } from '@dnd-kit/sortable';
import FormForgeApiApi from "../api/FormForgeApiApi";
import { createEmptyField } from "../constants";
import { v4 as uuidv4 } from 'uuid';

export default function useFormForgeDesigner(form, onFormUpdate) {
  const [layout, setLayout] = useState([]);
  const [selectedFieldId, setSelectedFieldId] = useState(null);
  const [viewMode, setViewMode] = useState("design");

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

  useEffect(() => {
    if (form?.fields && form.fields.length > 0) {
      setLayout([{
        id: `section-${form.id}`, title: "Form Alanları",
        rows: [{ id: `row-${form.id}-1`, fields: [...form.fields].sort((a, b) => a.order - b.order) }],
      }]);
    } else if (form) { 
      setLayout([{ id: `section-${form.id}`, title: "Form Alanları", rows: [{ id: `row-${form.id}-1`, fields: [] }] }]);
    } else {
      setLayout([]);
    }
  }, [form]);

  const handleSelectField = useCallback((fieldId) => {
    setSelectedFieldId(prevId => (prevId === fieldId ? null : fieldId));
  }, []);

  const handleUpdateField = useCallback(async (fieldData) => {
    if (!form?.id || !fieldData?.id || String(fieldData.id).includes('temp_')) return;
    setLayout(prevLayout => {
      const newLayout = JSON.parse(JSON.stringify(prevLayout));
      for (const section of newLayout) {
        for (const row of section.rows) {
          const fieldIndex = row.fields.findIndex(f => f.id === fieldData.id);
          if (fieldIndex !== -1) {
            row.fields[fieldIndex] = fieldData;
            break; 
          }
        }
      }
      return newLayout;
    });
    try {
      await FormForgeApiApi.updateFormField(fieldData.id, fieldData);
    } catch (error) {
      console.error("Alan güncellenirken bir hata oluştu.", error);
      onFormUpdate(form.id); 
    }
  }, [form?.id, onFormUpdate]);

  const handleDeleteField = useCallback(async (fieldId) => {
    if (!form?.id || !fieldId) return;
    if (!window.confirm("Bu alanı silmek istediğinizden emin misiniz?")) return;
    
    setLayout(prevLayout => {
      const newLayout = JSON.parse(JSON.stringify(prevLayout));
      newLayout.forEach(section => {
        section.rows.forEach(row => {
          row.fields = row.fields.filter(f => f.id !== fieldId);
        });
      });
      return newLayout;
    });

    try {
      await FormForgeApiApi.deleteFormField(fieldId);
      await onFormUpdate(form.id); // API'den güncel sıralamayı çek
    } catch (error) {
      console.error("Alan silinirken bir hata oluştu.", error);
      onFormUpdate(form.id);
    }
  }, [form?.id, onFormUpdate]);

  const handleAddRow = useCallback((sectionId) => {
    setLayout(prevLayout => {
      const newLayout = JSON.parse(JSON.stringify(prevLayout));
      const section = newLayout.find(s => s.id === sectionId);
      if (section) {
        section.rows.push({ id: `row_${uuidv4()}`, fields: [] });
      }
      return newLayout;
    });
  }, []);
  
  const handleDragEnd = useCallback(async (event) => {
    const { active, over } = event;
    if (!over) return;

    const originalLayout = JSON.parse(JSON.stringify(layout));
    let newLayout = JSON.parse(JSON.stringify(layout));

    const findContainer = (layout, id) => {
      for (const section of layout) {
        for (const row of section.rows) {
          if (row.id === id || row.fields.some(f => f.id === id)) return row;
        }
      }
      return null;
    };

    const isPaletteItem = active.data.current?.isPaletteItem === true;
    const overContainer = findContainer(newLayout, over.id);
    
    if (!overContainer) return; // Geçerli bir bırakma alanı yoksa işlemi iptal et.

    if (isPaletteItem) {
      const fieldType = active.data.current.fieldType;
      const newField = { ...createEmptyField({ type: fieldType }), form: form.id };
      
      const overIndex = over.id === overContainer.id
        ? overContainer.fields.length
        : overContainer.fields.findIndex(f => f.id === over.id);
      
      overContainer.fields.splice(overIndex, 0, newField);
    } else {
      const activeContainer = findContainer(newLayout, active.id);
      if (!activeContainer || active.id === over.id) return;

      const activeIndex = activeContainer.fields.findIndex(f => f.id === active.id);
      const [movedField] = activeContainer.fields.splice(activeIndex, 1);

      if (activeContainer.id === overContainer.id) {
        const overIndex = overContainer.fields.findIndex(f => f.id === over.id);
        overContainer.fields.splice(overIndex, 0, movedField);
      } else {
        const overIndex = over.id === overContainer.id
          ? overContainer.fields.length
          : overContainer.fields.findIndex(f => f.id === over.id);
        overContainer.fields.splice(overIndex, 0, movedField);
      }
    }

    setLayout(newLayout);

    let currentOrder = 0;
    const allFieldsInOrder = newLayout.flatMap(s => s.rows.flatMap(r => r.fields));
    const payload = allFieldsInOrder.map(field => {
        const fieldData = { ...field, order: currentOrder };
        currentOrder++;
        return fieldData;
    });

    const createPayload = payload.find(f => String(f.id).includes('temp_'));
    const orderPayload = payload.filter(f => !String(f.id).includes('temp_')).map(f => ({ id: f.id, order: f.order }));

    try {
      if (createPayload) {
        const { id, ...apiData } = createPayload;
        await FormForgeApiApi.createFormField(apiData);
      }
      if (orderPayload.length > 0 && !isPaletteItem) { // Sadece sıralama değiştiyse
          await FormForgeApiApi.updateFormFieldOrder(orderPayload);
      }
      // Her başarılı sürükle-bırak sonrası, yeni ID'leri ve doğru sıralamayı almak için formu yeniden çek.
      await onFormUpdate(form.id);
    } catch (error) {
      console.error("Sürükle-bırak işlemi sonrası API hatası:", error);
      setLayout(originalLayout);
    }
  }, [form, layout, onFormUpdate]);

  return {
    layout, selectedFieldId, viewMode, setViewMode, selectedField,
    onDragEnd: handleDragEnd, handleSelectField, handleUpdateField, handleDeleteField,
    handleAddRow
  };
}