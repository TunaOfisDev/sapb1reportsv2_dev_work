// path: frontend/src/components/NexusCore/containers/ReportPlayground/index.jsx

import React, { useState, useEffect, useCallback } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { DndContext, closestCenter, PointerSensor, useSensor, useSensors } from '@dnd-kit/core';
import { SortableContext, useSortable, arrayMove, verticalListSortingStrategy } from '@dnd-kit/sortable';
import { v4 as uuidv4 } from 'uuid';
import styles from './ReportPlayground.module.scss';

// Hook'lar, API'ler ve Ortak Bileşenler
import { useApi } from '../../hooks/useApi';
import { useNotifications } from '../../hooks/useNotifications';
import * as virtualTablesApi from '../../api/virtualTablesApi';
import * as reportTemplatesApi from '../../api/reportTemplatesApi';
import { MoreVertical, Eye, EyeOff } from 'react-feather';
import Spinner from '../../components/common/Spinner/Spinner';
import Button from '../../components/common/Button/Button';
import Input from '../../components/common/Input/Input';
import Table from '../../components/common/Table/Table';

// Her bir kolonu yöneten, kendi içinde interaktif olan alt bileşen
const SortableColumnItem = ({ col, onUpdate }) => {
    const { attributes, listeners, setNodeRef, transform, transition, isDragging } = useSortable({ id: col.id });
    const style = {
        transform: transform ? `translate3d(0, ${transform.y}px, 0)` : undefined,
        transition,
        opacity: isDragging ? 0.5 : 1, // Sürüklenirken şeffaflaştır
    };

    return (
        <li ref={setNodeRef} style={style} className={`${styles.columnManagerItem} ${isDragging ? styles.dragging : ''}`}>
            <span {...listeners} {...attributes} className={styles.dragHandle}><MoreVertical /></span>
            <div className={styles.columnEditor}>
                <Input 
                    id={`label-${col.id}`}
                    value={col.label}
                    onChange={(e) => onUpdate(col.key, { label: e.target.value })}
                />
            </div>
            <button 
                className={`${styles.visibilityToggle} ${col.visible ? styles.visible : ''}`}
                onClick={() => onUpdate(col.key, { visible: !col.visible })}
                title={col.visible ? 'Kolonu Gizle' : 'Kolonu Göster'}
            >
                {col.visible ? <Eye size={18} /> : <EyeOff size={18} />}
            </button>
        </li>
    );
};

const ReportPlayground = () => {
    const { virtualTableId } = useParams();
    const navigate = useNavigate();
    const { addNotification } = useNotifications();

    const { data: sourceData, loading: sourceLoading, error: sourceError, request: executeSourceQuery } = useApi(virtualTablesApi.executeVirtualTable);
    const { loading: isSaving, request: createReport } = useApi(reportTemplatesApi.createReportTemplate);

    const [reportTitle, setReportTitle] = useState('');
    const [reportColumns, setReportColumns] = useState([]);
    const [reportType, setReportType] = useState('detail');

    const memoizedExecuteQuery = useCallback(executeSourceQuery, []);
    useEffect(() => {
        if (virtualTableId) {
            memoizedExecuteQuery(virtualTableId);
        }
    }, [virtualTableId, memoizedExecuteQuery]);

    useEffect(() => {
        if (sourceData?.columns) {
            setReportTitle(reportTitle || `Yeni Rapor`);
            setReportColumns(sourceData.columns.map(colName => ({
                id: uuidv4(),
                key: colName,
                label: colName,
                visible: true,
            })));
        }
    }, [sourceData]);

    const handleColumnUpdate = (key, newProps) => {
        setReportColumns(items => items.map(col => 
            col.key === key ? { ...col, ...newProps } : col
        ));
    };

    const sensors = useSensors(useSensor(PointerSensor, { activationConstraint: { distance: 5 } }));

    const handleDragEnd = (event) => {
        const { active, over } = event;
        if (over && active.id !== over.id) {
            setReportColumns((items) => {
                const oldIndex = items.findIndex(item => item.id === active.id);
                const newIndex = items.findIndex(item => item.id === over.id);
                return arrayMove(items, oldIndex, newIndex);
            });
        }
    };

    const handleSave = async () => {
        if (!reportTitle) { /* ... */ }

        // ### GÜNCELLEME: Kaydedilen JSON'a rapor türünü ekliyoruz ###
        const configuration_json = {
            report_type: reportType,
            columns: reportColumns.map(({ key, label, visible }) => ({ key, label, visible })),
            // pivot_config: reportType === 'pivot' ? { ... } : {} // Pivot state'i eklendiğinde
        };
        const payload = {
            title: reportTitle,
            source_virtual_table_id: virtualTableId,
            configuration_json,
            sharing_status: 'PRIVATE',
        };
        const { success, data } = await createReport(payload);
        if (success) {
            addNotification('Rapor başarıyla kaydedildi!', 'success');
            navigate('/nexus/reports');
        } else {
            addNotification('Rapor kaydedilirken bir hata oluştu.', 'error');
        }
    };

    const getPreviewData = () => {
        if (!sourceData || !sourceData.rows || reportColumns.length === 0) return null;

        const visibleColumns = reportColumns.filter(c => c.visible);
        if (visibleColumns.length === 0) return { columns: [], rows: [] };

        const finalColumns = visibleColumns.map(c => c.label);
        const colIndexMap = sourceData.columns.reduce((acc, colName, index) => { acc[colName] = index; return acc; }, {});
        const finalColIndices = visibleColumns.map(c => colIndexMap[c.key]);
        const finalRows = sourceData.rows.map(row => finalColIndices.map(index => row[index]));

        return { columns: finalColumns, rows: finalRows };
    };

    if (sourceLoading) return <Spinner size="lg" />;
    if (sourceError) return <div className={styles.error}>Kaynak veri yüklenirken bir hata oluştu.</div>;

    return (
        <div className={styles.pageContainer}>
            <header className={styles.pageHeader}>
                <Input /* ... */ />
                
                {/* ### YENİ: Mod Değiştirme Düğmeleri ### */}
                <div className={styles.modeSwitcher}>
                    <button 
                        className={`${styles.modeButton} ${reportType === 'detail' ? styles.active : ''}`}
                        onClick={() => setReportType('detail')}
                    >
                        Detay Tablo
                    </button>
                    <button 
                        className={`${styles.modeButton} ${reportType === 'pivot' ? styles.active : ''}`}
                        onClick={() => setReportType('pivot')}
                    >
                        Özet (Pivot) Tablo
                    </button>
                </div>

                <Button onClick={handleSave} variant="primary" disabled={isSaving}>
                    {isSaving ? 'Kaydediliyor...' : 'Raporu Kaydet'}
                </Button>
            </header>

            <DndContext /* ... */ >
                <div className={styles.playgroundContainer}>
                    {/* ### YENİ: Arayüz artık seçilen moda göre değişiyor ### */}
                    {reportType === 'detail' ? (
                        <>
                            {/* SOL PANEL: KOLON YÖNETİCİSİ */}
                            <div className={styles.panel}>
                                <h3 className={styles.panelTitle}>Kolon Yöneticisi</h3>
                                <div className={styles.panelContent}>
                                    <SortableContext items={reportColumns.map(c => c.id)} strategy={verticalListSortingStrategy}>
                                        <ul className={styles.columnManagerList}>
                                            {reportColumns.map(col => (
                                                <SortableColumnItem key={col.id} col={col} onUpdate={handleColumnUpdate} />
                                            ))}
                                        </ul>
                                    </SortableContext>
                                </div>
                            </div>
                            {/* SAĞ PANEL: CANLI ÖNİZLEME */}
                            <div className={styles.panel}>
                                 <h3 className={styles.panelTitle}>Canlı Önizleme</h3>
                                 <div className={styles.tableWrapper}>
                                    <Table data={getPreviewData()} />
                                 </div>
                            </div>
                        </>
                    ) : (
                        <>
                            {/* SOL PANEL: KULLANILABİLİR KOLONLAR */}
                            <div className={styles.panel}>
                                <h3 className={styles.panelTitle}>Kullanılabilir Kolonlar</h3>
                                {/* Burası, pivot için sürükle-bırak kaynak kolonları listesi olacak */}
                            </div>
                            {/* SAĞ PANEL: PIVOT ALANLARI */}
                            <div className={styles.panel}>
                                <h3 className={styles.panelTitle}>Pivot Alanları</h3>
                                <div className={`${styles.panelContent} ${styles.pivotLayoutContainer}`}>
                                    <div className={`${styles.dropZone} ${styles.rows}`}>
                                        <h4 className={styles.dropZoneTitle}>Satırlar</h4>
                                    </div>
                                    <div className={`${styles.dropZone} ${styles.columns}`}>
                                        <h4 className={styles.dropZoneTitle}>Sütunlar</h4>
                                    </div>
                                    <div className={`${styles.dropZone} ${styles.values}`}>
                                        <h4 className={styles.dropZoneTitle}>Değerler</h4>
                                    </div>
                                </div>
                            </div>
                        </>
                    )}
                </div>
            </DndContext>
        </div>
    );
};

export default ReportPlayground;