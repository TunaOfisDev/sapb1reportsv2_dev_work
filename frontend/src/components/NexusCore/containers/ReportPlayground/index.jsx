// path: frontend/src/components/NexusCore/containers/ReportPlayground/index.jsx

import React, { useState, useEffect, useCallback } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { DndContext, closestCenter, DragOverlay, PointerSensor, useSensor, useSensors } from '@dnd-kit/core';
import { SortableContext, arrayMove, verticalListSortingStrategy } from '@dnd-kit/sortable';
import { v4 as uuidv4 } from 'uuid';
import styles from './ReportPlayground.module.scss';

// Hook'lar, API'ler ve Bileşenler
import { useApi } from '../../hooks/useApi';
import { useNotifications } from '../../hooks/useNotifications';
import * as virtualTablesApi from '../../api/virtualTablesApi';
import * as reportTemplatesApi from '../../api/reportTemplatesApi';
import AvailableColumns from './AvailableColumns';
import ReportCanvas from './ReportCanvas';
import PropertiesPanel from './PropertiesPanel';
import Spinner from '../../components/common/Spinner/Spinner';
import Button from '../../components/common/Button/Button';
import Input from '../../components/common/Input/Input';

const ReportPlayground = () => {
    const { virtualTableId } = useParams();
    const navigate = useNavigate();
    const { addNotification } = useNotifications();

    // API Hook'ları
    const { data: sourceData, loading: sourceLoading, error: sourceError, request: executeSourceQuery } = useApi(virtualTablesApi.executeVirtualTable);
    const { loading: isSaving, request: createReport } = useApi(reportTemplatesApi.createReportTemplate);

    // State Yönetimi
    const [reportTitle, setReportTitle] = useState('');
    const [reportColumns, setReportColumns] = useState([]); // Tuvaldeki kolonlar
    const [selectedColumnKey, setSelectedColumnKey] = useState(null);
    const [activeId, setActiveId] = useState(null); // Sürüklenen aktif elemanı tutar

    // Veri Çekme
    const memoizedExecuteQuery = useCallback(executeSourceQuery, []);
    useEffect(() => {
        if (virtualTableId) {
            memoizedExecuteQuery(virtualTableId);
        }
    }, [virtualTableId, memoizedExecuteQuery]);
    
    // Olay Yöneticileri (Event Handlers)
    const handleAddColumn = useCallback((columnKey) => {
        if (reportColumns.some(c => c.key === columnKey)) {
            addNotification(`'${columnKey}' kolonu zaten raporda mevcut.`, 'info');
            return;
        }
        const newColumn = { key: columnKey, label: columnKey, visible: true, id: uuidv4() };
        setReportColumns((items) => [...items, newColumn]);
    }, [reportColumns, addNotification]);

    const handleRemoveColumn = useCallback((keyToRemove) => {
        setReportColumns(items => items.filter(col => col.key !== keyToRemove));
        if (selectedColumnKey === keyToRemove) {
            setSelectedColumnKey(null);
        }
    }, [selectedColumnKey, reportColumns]);

    const sensors = useSensors(
        useSensor(PointerSensor, {
            activationConstraint: { distance: 8 },
        })
    );
    
    const handleDragStart = (event) => {
        setActiveId(event.active.id);
    };
    
    const handleDragEnd = (event) => {
        const { active, over } = event;
        setActiveId(null);
        if (!over) return;

        if (over.id === 'canvas-drop-area' && !reportColumns.some(c => c.key === active.id)) {
            handleAddColumn(active.id);
            return;
        }
        
        const activeItemInCanvas = reportColumns.find(c => c.id === active.id);
        const overItemInCanvas = reportColumns.find(c => c.id === over.id);

        if (activeItemInCanvas && overItemInCanvas && active.id !== over.id) {
            setReportColumns((items) => {
                const oldIndex = items.findIndex(item => item.id === active.id);
                const newIndex = items.findIndex(item => item.id === over.id);
                return arrayMove(items, oldIndex, newIndex);
            });
        }
    };
    
    const handleUpdateColumn = (key, newProps) => {
        setReportColumns(items => items.map(col => 
            col.key === key ? { ...col, ...newProps } : col
        ));
    };

    const handleSave = async () => {
        if (!reportTitle) {
            addNotification('Lütfen rapora bir başlık verin.', 'error');
            return;
        }
        const configuration_json = {
            columns: reportColumns.map(({ key, label, visible }) => ({ key, label, visible })),
        };
        const payload = {
            title: reportTitle,
            source_virtual_table_id: virtualTableId,
            configuration_json,
            sharing_status: 'PRIVATE',
        };
        const { success } = await createReport(payload);
        if (success) {
            addNotification('Rapor başarıyla kaydedildi!', 'success');
            navigate('/nexus/reports');
        } else {
            addNotification('Rapor kaydedilirken bir hata oluştu.', 'error');
        }
    };
    
    if (sourceLoading) return <Spinner size="lg" />;
    if (sourceError) return <div className={styles.error}>Kaynak veri yüklenirken bir hata oluştu. Lütfen geçerli bir Sanal Tablo ID'si ile geldiğinizden emin olun.</div>;

    const selectedColumn = reportColumns.find(c => c.key === selectedColumnKey) || null;
    const activeItem = activeId ? (reportColumns.find(c => c.id === activeId) || { key: activeId, label: activeId }) : null;

    return (
        <DndContext 
            onDragStart={handleDragStart}
            onDragEnd={handleDragEnd} 
            collisionDetection={closestCenter}
            sensors={sensors}
        >
            <div className={styles.pageContainer}>
                <header className={styles.pageHeader}>
                    <Input 
                        id="report-title"
                        label="Rapor Başlığı"
                        value={reportTitle}
                        onChange={(e) => setReportTitle(e.target.value)}
                        placeholder="Örn: Aylık Müşteri Risk Analizi"
                    />
                    <Button onClick={handleSave} variant="primary" disabled={isSaving}>
                        {isSaving ? 'Kaydediliyor...' : 'Raporu Kaydet'}
                    </Button>
                </header>
                <div className={styles.playgroundContainer}>
                    <AvailableColumns 
                        columns={sourceData?.columns || []}
                        onColumnAdd={handleAddColumn} 
                    />
                    <SortableContext items={reportColumns.map(c => c.id)} strategy={verticalListSortingStrategy}>
                        <ReportCanvas 
                            columns={reportColumns}
                            data={sourceData || {}}
                            onColumnClick={setSelectedColumnKey}
                            selectedColumnKey={selectedColumnKey}
                            onColumnRemove={handleRemoveColumn}
                        />
                    </SortableContext>
                    <PropertiesPanel 
                        selectedColumn={selectedColumn}
                        onUpdateColumn={handleUpdateColumn}
                    />
                </div>
            </div>
            <DragOverlay>
                {activeId ? (
                    <div className={`${styles.columnItem} ${styles.dragging}`}>
                        {activeItem?.label || activeId}
                    </div>
                ) : null}
            </DragOverlay>
        </DndContext>
    );
};

export default ReportPlayground;