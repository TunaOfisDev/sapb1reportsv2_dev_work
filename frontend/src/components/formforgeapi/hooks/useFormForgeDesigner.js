// path: frontend/src/components/formforgeapi/hooks/useFormForgeDesigner.js

import { useState, useEffect, useMemo, useCallback } from "react";
import { arrayMove } from '@dnd-kit/sortable';
import FormForgeApiApi from "../api/FormForgeApiApi";
import { v4 as uuidv4 } from 'uuid';

export default function useFormForgeDesigner(form, onFormUpdate) {
  const [layout, setLayout] = useState([]);
  const [selectedFieldId, setSelectedFieldId] = useState(null);
  const [viewMode, setViewMode] = useState("design");

  const selectedField = useMemo(() => {
    if (!selectedFieldId || !layout || layout.length === 0) return null;
    return layout[0].rows[0].fields.find((f) => f.id === selectedFieldId) || null;
  }, [selectedFieldId, layout]);

  useEffect(() => {
    // Form verisi geldiğinde veya değiştiğinde layout'u oluştur/güncelle
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
    } else {
      // Form yüklenmediyse veya boşsa, layout'u boş bir yapı ile başlat
      // Bu, boş tuvale eleman eklerken çökmesini engeller.
      if (form) { // 'form' nesnesi var ama 'fields' yoksa (yeni oluşturulmuş boş form)
          setLayout([{
              id: `section-${form.id}`,
              title: "Form Alanları",
              rows: [{ id: `row-${form.id}-1`, fields: [] }],
          }]);
      } else {
          setLayout([]); // Form yükleniyor...
      }
    }
  }, [form]);

  const handleSelectField = useCallback((fieldId) => setSelectedFieldId(fieldId), []);

  const handleUpdateField = useCallback(async (fieldData) => {
    if (!form?.id || !fieldData?.id) return;
    try {
      await FormForgeApiApi.updateFormField(fieldData.id, fieldData);
      onFormUpdate(form.id);
    } catch (error) {
      console.error("Alan güncellenirken bir hata oluştu.", error);
    }
  }, [form, onFormUpdate]);

  const handleDeleteField = useCallback(async (fieldId) => {
    if (!form?.id || !fieldId) return;
    if (!window.confirm("Bu alanı silmek istediğinizden emin misiniz?")) return;
    try {
      await FormForgeApiApi.deleteFormField(fieldId);
      onFormUpdate(form.id);
    } catch (error) {
      console.error("Alan silinirken bir hata oluştu.", error);
    }
  }, [form, onFormUpdate]);

  const handleDragEnd = useCallback(async (event) => {
    const { active, over } = event;

    // Eğer bir bırakma alanı yoksa veya form henüz yüklenmemişse hiçbir şey yapma
    if (!over || !form) return;
    
    const isPaletteDrag = active.data.current?.isPaletteItem === true;
    const isReordering = !isPaletteDrag;

    // --- SENARYO 1: Paletten yeni bir alan ekleniyor ---
    if (isPaletteDrag) {
      const fieldType = active.data.current.fieldType;
      const targetRow = layout[0]?.rows[0] ?? { id: `row-${form.id}-1`, fields: [] };
      
      let newIndex = targetRow.fields.length; // Varsayılan: Sona ekle
      const overFieldIndex = targetRow.fields.findIndex(f => f.id === over.id);

      if (overFieldIndex !== -1) {
        newIndex = overFieldIndex; // Eğer bir alanın üzerine bırakıldıysa, o index'e ekle
      }

      const newFieldData = {
        form: form.id,
        label: `Yeni ${fieldType}`,
        field_type: fieldType,
        order: newIndex,
        options: ['singleselect', 'multiselect', 'radio'].includes(fieldType) ? [] : [],
      };
      
      // Arayüzü anında güncelle (Optimistic Update)
      const tempField = { ...newFieldData, id: `temp-${uuidv4()}` };
      setLayout(prevLayout => {
          const newLayout = prevLayout.length > 0 ? JSON.parse(JSON.stringify(prevLayout)) : [{ id: `section-${form.id}`, title: "Form Alanları", rows: [{ id: `row-${form.id}-1`, fields: [] }] }];
          const fields = newLayout[0].rows[0].fields;
          fields.splice(newIndex, 0, tempField);
          return newLayout;
      });

      // API isteğini gönder
      try {
        await FormForgeApiApi.createFormField(newFieldData);
        onFormUpdate(form.id);
      } catch (error) {
        console.error("Alan eklenirken hata oluştu.", error);
        setLayout(layout); // Hata durumunda değişikliği geri al
      }
    }

    // --- SENARYO 2: Tuval içinde mevcut bir alan sıralanıyor ---
    if (isReordering) {
      if (active.id === over.id) return;

      const activeRow = layout[0]?.rows[0];
      if (!activeRow) return;

      const oldIndex = activeRow.fields.findIndex(f => f.id === active.id);
      const newIndex = activeRow.fields.findIndex(f => f.id === over.id);
      if (oldIndex === -1 || newIndex === -1) return;

      const reorderedFields = arrayMove(activeRow.fields, oldIndex, newIndex);
      
      setLayout(prevLayout => {
        const newLayout = JSON.parse(JSON.stringify(prevLayout));
        newLayout[0].rows[0].fields = reorderedFields;
        return newLayout;
      });
      
      const orderPayload = reorderedFields.map((field, index) => ({
        id: field.id,
        order: index
      }));
      
      try {
        await FormForgeApiApi.updateFormFieldOrder(orderPayload);
      } catch (error) {
        console.error("Sıralama güncellenirken hata oluştu.", error);
        setLayout(layout); // Değişikliği geri al
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
  };
}