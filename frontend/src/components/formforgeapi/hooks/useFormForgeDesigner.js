// path: frontend/src/components/formforgeapi/hooks/useFormForgeDesigner.js

import { useState, useEffect, useMemo, useCallback } from "react";
import FormForgeApiApi from "../api/FormForgeApiApi";
import { createEmptyField } from "../constants";
import { v4 as uuidv4 } from 'uuid';

/**
 * FormForge Tasarımcısı için tüm UI mantığını ve state'i yöneten merkezi hook.
 * @param {object} form - Dışarıdan gelen, backend'den çekilmiş form nesnesi.
 * @param {function} onFormUpdate - Bir alan oluşturulduğunda veya kritik bir hata olduğunda,
 * ana formu yeniden çekmek için kullanılacak callback fonksiyonu.
 */
export default function useFormForgeDesigner(form, onFormUpdate) {
    // --- STATE TANIMLARI ---
    const [layout, setLayout] = useState([]); // Formun görsel düzenini tutar (seksiyonlar, satırlar, alanlar)
    const [selectedFieldId, setSelectedFieldId] = useState(null); // Düzenlenmek üzere seçilen alanın ID'si
    const [viewMode, setViewMode] = useState("design"); // 'design' | 'preview'

    // --- EFFECT'LER ---
    // Dışarıdan gelen 'form' prop'u değiştiğinde, layout'u yeniden oluşturur.
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
    }, [form]); // Sadece ana form nesnesi değiştiğinde tetiklenir.

    // --- MEMOIZED DEĞERLER ---
    // Seçili alan nesnesini, her render'da tekrar hesaplamamak için useMemo ile alır.
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

    // --- CALLBACK FONKSİYONLARI ---

    // Bir alana tıklandığında seçili alanı ayarlar.
    const handleSelectField = useCallback((fieldId) => {
        setSelectedFieldId(prevId => (prevId === fieldId ? null : fieldId));
    }, []);

    // Bir alanın özelliklerini günceller. (Label silinme sorunu burada çözüldü)
    const handleUpdateField = useCallback(async (fieldData) => {
        // 1. İyimser Güncelleme: Arayüzü anında yeni veriyle günceller.
        setLayout(prevLayout =>
            prevLayout.map(section => ({
                ...section,
                rows: section.rows.map(row => ({
                    ...row,
                    fields: row.fields.map(f => f.id === fieldData.id ? fieldData : f),
                })),
            }))
        );

        // 2. API Çağrısı: Arka planda değişikliği kaydeder.
        if (String(fieldData.id).includes('temp_')) return; // Geçici alanları kaydetme
        try {
            await FormForgeApiApi.updateFormField(fieldData.id, fieldData);
            // Başarılı olursa, tüm formu yeniden çekmeye gerek YOKTUR. Çünkü en güncel veri zaten bizde.
        } catch (error) {
            console.error("Alan güncellenirken bir hata oluştu.", error);
            // Hata durumunda, veri tutarlılığı için formu sunucudan yeniden çek.
            onFormUpdate(form.id); 
        }
    }, [form?.id, onFormUpdate]);

    // Bir alanı siler.
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
        setSelectedFieldId(null);

        try {
            await FormForgeApiApi.deleteFormField(fieldId);
            await onFormUpdate(form.id); // Silme sonrası yeniden çekmek, sıralamayı garantiler.
        } catch (error) {
            console.error("Alan silinirken bir hata oluştu.", error);
            onFormUpdate(form.id);
        }
    }, [form?.id, onFormUpdate]);

    // Sürükle-bırak işlemini yönetir. (Anında güncelleme sorunu burada çözüldü)
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

        // API çağrılarını state güncellemesi bittikten sonra yap
        try {
            const allFields = finalLayout.flatMap(s => s.rows.flatMap(r => r.fields));
            const payload = allFields.map((field, index) => ({ ...field, order: index }));

            const newFieldPayload = payload.find(f => String(f.id).includes('temp_'));
            
            if (newFieldPayload) {
                const { id, ...apiData } = newFieldPayload;
                await FormForgeApiApi.createFormField(apiData);
                await onFormUpdate(form.id); // Yeni alan eklendiğinde ID'leri almak için formu yeniden çek.
            } else {
                const orderPayload = payload.map(({ id, order }) => ({ id, order }));
                await FormForgeApiApi.updateFormFieldOrder(orderPayload);
                // Sıralama sonrası formu yeniden çekmeye gerek yok, UI zaten güncel.
            }
        } catch (error) {
            console.error("Sürükle-bırak sonrası hata:", error);
            onFormUpdate(form.id);
        }
    }, [form, onFormUpdate]);

    // Yeni bir satır ekler.
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

    // --- HOOK'UN DIŞARIYA AÇTIĞI ARAYÜZ ---
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