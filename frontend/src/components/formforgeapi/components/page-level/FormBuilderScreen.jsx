// path: frontend/src/components/formforgeapi/components/page-level/FormBuilderScreen.jsx

import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { DndContext, PointerSensor, useSensor, useSensors, closestCenter } from '@dnd-kit/core';

import useFormForgeApi from '../../hooks/useFormForgeApi';
import useFormForgeDesigner from '../../hooks/useFormForgeDesigner';

import FieldPalette from '../palette/FieldPalette';
import FormCanvas from '../canvas/FormCanvas';
import FieldPropsDrawer from '../properties/FieldPropsDrawer';

import styles from '../../css/FormBuilderScreen.module.css';
import previewStyles from '../../css/FormFillScreen.module.css';

// Önizleme Arayüzünü Render Eden STATİK ve GÖRSEL Yardımcı Bileşen
const PreviewRenderer = ({ form }) => {
  if (!form?.fields || form.fields.length === 0) {
    return (
      <div className={previewStyles.formFillScreen} style={{background: 'white', padding: '2rem', textAlign: 'center'}}>
        <p>Önizleme için forma alan ekleyin.</p>
      </div>
    );
  }

  const renderField = (field) => {
    const fieldId = String(field.id);
    const commonProps = {
      id: fieldId,
      className: previewStyles.formFillScreen__control,
      disabled: true, // Bütün alanları devre dışı bırakır
    };

    return (
      <div key={fieldId} className={previewStyles.formFillScreen__group}>
        <label htmlFor={fieldId} className={previewStyles.formFillScreen__label}>
          {field.label} {field.is_required && '*'}
        </label>
        {(() => {
          switch (field.field_type) {
            case 'textarea':
              return <textarea {...commonProps} />;
            case 'multiselect':
              return (
                <select {...commonProps} multiple>
                  {field.options.map(opt => <option key={opt.id} value={opt.label}>{opt.label}</option>)}
                </select>
              );
            case 'singleselect':
              return (
                <select {...commonProps}>
                  <option value="">Seçiniz...</option>
                  {field.options.map(opt => <option key={opt.id} value={opt.label}>{opt.label}</option>)}
                </select>
              );
            case 'checkbox':
               return ( <div style={{marginTop: '0.5rem'}}><label><input type="checkbox" {...commonProps} /> {field.label}</label></div> );
            case 'radio':
              return <div style={{marginTop: '0.5rem'}}>{field.options.map(opt => ( <label key={opt.id} className={previewStyles.formFillScreen__inlineLabel}><input type="radio" name={fieldId} {...commonProps} /> {opt.label}</label> ))}</div>;
            default:
              return <input type={field.field_type} {...commonProps} />;
          }
        })()}
      </div>
    );
  };

  return (
    <div className={previewStyles.formFillScreen} style={{background: 'white', padding: '2rem'}}>
      <div className={previewStyles.formFillScreen__form}>
        {form.fields.sort((a, b) => a.order - b.order).map(renderField)}
      </div>
    </div>
  );
};


// Ana FormBuilderScreen Bileşeni
const FormBuilderScreen = () => {
  const { formId } = useParams();
  const navigate = useNavigate();
  const isNewMode = formId === 'new';

  const {
    currentForm, loading, error, fetchForm, createForm,
    departments, fetchDepartments
  } = useFormForgeApi();
  
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
      activationConstraint: {
        distance: 8,
      },
    })
  );

  if (isNewMode) {
    return (
      <div style={{ padding: '2rem', maxWidth: '500px', margin: 'auto' }}>
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

  if (loading && !currentForm) return <div>Yükleniyor...</div>;
  if (error) return <div className="alert alert-danger">Hata: {error}</div>;
  if (!currentForm) return <div>Form bulunamadı veya yüklenemedi.</div>;

  return (
    <DndContext
      sensors={sensors}
      collisionDetection={closestCenter}
      onDragEnd={designer.onDragEnd}
    >
      <div className={`${styles.formBuilderScreen} ${styles[`formBuilderScreen--${designer.viewMode}`]}`}>
        <header className={styles.formBuilderScreen__header}>
          <h1 className={styles.formBuilderScreen__logo}>{currentForm.title}</h1>
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
                  />
              ) : (
                  <PreviewRenderer form={currentForm} />
              )}
            </div>

            {designer.viewMode === 'design' && (
                <div className={styles.formBuilderScreen__drawerSlot}>
                    <FieldPropsDrawer
                        field={designer.selectedField}
                        onClose={() => designer.handleSelectField(null)}
                        onUpdate={designer.handleUpdateField}
                        onDelete={designer.handleDeleteField}
                    />
                </div>
            )}
        </div>
      </div>
    </DndContext>
  );
};

export default FormBuilderScreen;