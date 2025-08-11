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
    // Çoklu satır ve bölüm desteği için güncellendi
    for (const section of layout) {
      for (const row of section.rows) {
        const field = row.fields.find(f => f.id === selectedFieldId);
        if (field) return field;
      }
    }
    return null;
  }, [selectedFieldId, layout]);

  useEffect(() => {
    if (form?.fields) {
      const initialLayout = [{
        id: `section-${form.id}`,
        title: "Form Alanları",
        rows: [{
          id: `row-${form.id}-1`,
          fields: [...form.fields].sort((a, b) => a.order - b.order),
        }],
      }];
      setLayout(initialLayout);
    } else if (form) { 
      setLayout([{
          id: `section-${form.id}`,
          title: "Form Alanları",
          rows: [{ id: `row-${form.id}-1`, fields: [] }],
      }]);
    } else {
      setLayout([]);
    }
  }, [form]);

  const handleSelectField = useCallback((fieldId) => setSelectedFieldId(fieldId), []);
  
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

  const handleUpdateField = useCallback(async (fieldData) => {
    if (!form?.id || !fieldData?.id || String(fieldData.id).includes('temp_')) return;
    
    setLayout(prevLayout => {
        const newLayout = JSON.parse(JSON.stringify(prevLayout));
        const section = newLayout.find(s => s.rows.some(r => r.fields.some(f => f.id === fieldData.id)));
        if (section) {
            const row = section.rows.find(r => r.fields.some(f => f.id === fieldData.id));
            if (row) {
                const fieldIndex = row.fields.findIndex(f => f.id === fieldData.id);
                if (fieldIndex !== -1) {
                    row.fields[fieldIndex] = fieldData;
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
      onFormUpdate(form.id);
    } catch (error) {
      console.error("Alan silinirken bir hata oluştu.", error);
      onFormUpdate(form.id);
    }
  }, [form?.id, onFormUpdate]);

  const handleDragEnd = useCallback(async (event) => {
    const { active, over } = event;
    if (!over || !form) return;
    
    const isPaletteDrag = active.data.current?.isPaletteItem === true;
    if (isPaletteDrag) { 
        // ... Yeni alan ekleme kodu ...
        return;
    }

    const isReordering = !isPaletteDrag;
    if (isReordering) {
        const activeId = active.id;
        const overId = over.id;
        if (activeId === overId) return;

        const originalLayout = JSON.parse(JSON.stringify(layout));
        let newLayout = JSON.parse(JSON.stringify(layout));

        const findContainer = (layout, id) => {
            for (const section of layout) {
                for (const row of section.rows) {
                    if (row.id === id || row.fields.some(f => f.id === id)) {
                        return row;
                    }
                }
            }
            return null;
        };

        const activeContainer = findContainer(newLayout, activeId);
        const overContainer = findContainer(newLayout, overId);

        if (!activeContainer || !overContainer) return;

        const activeIndex = activeContainer.fields.findIndex(f => f.id === activeId);
        const [movedField] = activeContainer.fields.splice(activeIndex, 1);
        
        const overIndex = overContainer.fields.findIndex(f => f.id === overId);
        overContainer.fields.splice(overIndex, 0, movedField);
        
        setLayout(newLayout);
        
        let currentOrder = 0;
        const orderPayload = [];
        for (const section of newLayout) {
            for (const row of section.rows) {
                for (const field of row.fields) {
                    orderPayload.push({ id: field.id, order: currentOrder });
                    currentOrder++;
                }
            }
        }
        
        try {
            await FormForgeApiApi.updateFormFieldOrder(orderPayload);
        } catch (error) {
            console.error("Sıralama güncellenirken hata oluştu. Değişiklikler geri alınıyor.", error);
            setLayout(originalLayout); 
        }
    }
  }, [layout, form, onFormUpdate]);

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
    handleAddRow
  };
}