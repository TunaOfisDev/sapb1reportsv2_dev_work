// path: frontend/src/components/formforgeapi/components/page-level/FormBuilderScreen.jsx

import React, { useEffect, useState } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { DndContext, PointerSensor, useSensor, useSensors, closestCenter } from '@dnd-kit/core';

import useFormForgeApi from '../../hooks/useFormForgeApi';
import useFormForgeDesigner from '../../hooks/useFormForgeDesigner';

import FieldPalette from '../palette/FieldPalette';
import FormCanvas from '../canvas/FormCanvas';
import FieldPropsDrawer from '../properties/FieldPropsDrawer';
import FormPreview from '../canvas/FormPreview';

import styles from '../../css/FormBuilderScreen.module.css';

const FormBuilderScreen = () => {
    const { formId } = useParams();
    const navigate = useNavigate();
    const isNewMode = formId === 'new';

    const {
        currentForm, loading, error, fetchForm, createForm,
        departments, fetchDepartments
    } = useFormForgeApi();

    // useFormForgeDesigner hook'u, tüm tasarım mantığını içeren 'designer' nesnesini döndürür.
    const designer = useFormForgeDesigner(currentForm, fetchForm);

    const [newFormTitle, setNewFormTitle] = useState('');
    const [newFormDept, setNewFormDept] = useState('');

    useEffect(() => {
        if (isNewMode) {
            fetchDepartments();
        } else {
            fetchForm(formId);
        }
    }, [formId, isNewMode, fetchDepartments, fetchForm]);

    const handleCreateForm = async (e) => {
        e.preventDefault();
        if (!newFormTitle || !newFormDept) {
            alert("Lütfen form başlığı ve departman seçiniz.");
            return;
        }
        await createForm({ title: newFormTitle, department: newFormDept });
    };

    const sensors = useSensors(
        useSensor(PointerSensor, {
            activationConstraint: { distance: 8 },
        })
    );
    
    // Yeni form oluşturma ekranı (değişiklik yok)
    if (isNewMode) {
        return (
            <div style={{ padding: '2rem', maxWidth: '500px', margin: 'auto' }}>
                <div style={{ marginBottom: '1.5rem' }}>
                    <Link to="/formforgeapi">&larr; Form Listesine Geri Dön</Link>
                </div>
                <h2>Yeni Form Oluştur</h2>
                <form onSubmit={handleCreateForm}>
                    <div className="mb-3">
                        <label htmlFor="formTitle" className="form-label">Form Başlığı</label>
                        <input
                            type="text" id="formTitle" className="form-control"
                            value={newFormTitle} onChange={(e) => setNewFormTitle(e.target.value)}
                            required />
                    </div>
                    <div className="mb-3">
                        <label htmlFor="formDept" className="form-label">Departman</label>
                        <select id="formDept" className="form-select" value={newFormDept}
                            onChange={(e) => setNewFormDept(e.target.value)} required >
                            <option value="" disabled>Seçiniz...</option>
                            {departments.map(d => <option key={d.id} value={d.id}>{d.name}</option>)}
                        </select>
                    </div>
                    <button type="submit" className="btn btn-primary" disabled={loading}>
                        {loading ? 'Oluşturuluyor...' : 'Oluştur ve Tasarıma Başla'}
                    </button>
                </form>
            </div>
        );
    }
    
    // Yüklenme ve hata durumları (değişiklik yok)
    if (loading && !currentForm) return <div>Yükleniyor...</div>;
    if (error) return <div className="alert alert-danger">Hata: {error}</div>;
    if (!currentForm) return <div>Form bulunamadı veya yüklenemedi.</div>;

    // Ana form tasarım ekranı
    return (
        <DndContext
            sensors={sensors}
            collisionDetection={closestCenter}
            onDragEnd={designer.onDragEnd}
        >
            <div className={`${styles.formBuilderScreen} ${styles[`formBuilderScreen--${designer.viewMode}`]}`}>
                <header className={styles.formBuilderScreen__header}>
                    <div className={styles.formBuilderScreen__navigation}>
                        <Link to="/formforgeapi" className={styles.formBuilderScreen__backLink}>&larr; Geri</Link>
                        <h1 className={styles.formBuilderScreen__logo}>{currentForm.title}</h1>
                    </div>
                    <div className={styles.formBuilderScreen__viewToggle}>
                        <button
                            onClick={() => designer.setViewMode('design')}
                            className={`${styles.formBuilderScreen__toggleBtn} ${designer.viewMode === 'design' ? styles['formBuilderScreen__toggleBtn--active'] : ''}`}
                        >
                            Tasarım
                        </button>
                        <button
                            onClick={() => designer.setViewMode('preview')}
                            className={`${styles.formBuilderScreen__toggleBtn} ${designer.viewMode === 'preview' ? styles['formBuilderScreen__toggleBtn--active'] : ''}`}
                        >
                            Önizleme
                        </button>
                    </div>
                    <div>
                        <button className="btn btn-primary" onClick={() => navigate('/formforgeapi')}>Kaydet ve Kapat</button>
                    </div>
                </header>

                <div className={styles.formBuilderScreen__layout}>
                    {designer.viewMode === 'design' && (
                        <div className={styles.formBuilderScreen__paletteSlot}>
                            <FieldPalette />
                        </div>
                    )}
                    
                    <div className={styles.formBuilderScreen__canvasSlot}>
                        {designer.viewMode === 'design' ? (
                            <FormCanvas
                                layout={designer.layout}
                                selectedFieldId={designer.selectedFieldId}
                                onSelectField={designer.handleSelectField}
                                onAddRow={designer.handleAddRow}
                            />
                        ) : (
                            <FormPreview
                                form={{
                                    ...currentForm,
                                    fields: designer.layout.flatMap(section =>
                                        section.rows.flatMap(row => row.fields)
                                    )
                                }}
                            />
                        )}
                    </div>

                    {designer.viewMode === 'design' && (
                        <div className={styles.formBuilderScreen__drawerSlot}>
                            <FieldPropsDrawer
                                field={designer.selectedField}
                                // DEĞİŞİKLİK: 'onClose' prop'u artık hook'tan gelen sabit referanslı fonksiyonu kullanıyor.
                                // Bu, FieldPropsDrawer'ın gereksiz yere render olmasını engeller.
                                onClose={designer.handleCloseDrawer}
                                onUpdate={designer.handleUpdateField}
                                onDelete={designer.handleDeleteField}
                                onAddOption={designer.handleAddOption}
                            />
                        </div>
                    )}
                </div>
            </div>
        </DndContext>
    );
};

export default FormBuilderScreen;