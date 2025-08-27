// path: frontend/src/components/NexusCore/containers/ReportPlayground/index.jsx

import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { DndContext, closestCenter } from '@dnd-kit/core';
import { arrayMove } from '@dnd-kit/sortable';
import { v4 as uuidv4 } from 'uuid';
import styles from './ReportPlayground.module.scss';

// Hook'lar ve API'ler
import { useApi } from '../../hooks/useApi';
import { useNotifications } from '../../hooks/useNotifications';
import * as virtualTablesApi from '../../api/virtualTablesApi';
import * as reportTemplatesApi from '../../api/reportTemplatesApi';

// Bileşenler
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

    // Kaynak veriyi ilk yüklemede çek
    useEffect(() => {
        if (virtualTableId) {
            executeSourceQuery(virtualTableId);
        }
    }, [virtualTableId, executeSourceQuery]);

    // Sürükle-bırak bittiğinde çalışan ana mantık
    const handleDragEnd = (event) => {
        const { active, over } = event;

        if (over && active.id !== over.id) {
            // Kolonları kendi içinde yeniden sıralama
            setReportColumns((items) => {
                const oldIndex = items.findIndex(item => item.key === active.id);
                const newIndex = items.findIndex(item => item.key === over.id);
                return arrayMove(items, oldIndex, newIndex);
            });
        } else if (over && over.id === 'canvas-drop-area' && !reportColumns.some(c => c.key === active.id)) {
            // Soldaki listeden tuvale yeni kolon ekleme
            const newColumnKey = active.id;
            const newColumn = {
                key: newColumnKey,
                label: newColumnKey,
                visible: true,
                id: uuidv4(), // Sıralama için benzersiz bir id
            };
            setReportColumns((items) => [...items, newColumn]);
        }
    };
    
    // Özellikler panelinden bir kolonu güncelleme
    const handleUpdateColumn = (key, newProps) => {
        setReportColumns(items => items.map(col => 
            col.key === key ? { ...col, ...newProps } : col
        ));
    };

    // Raporu kaydetme
    const handleSave = async () => {
        if (!reportTitle) {
            addNotification('Lütfen rapora bir başlık verin.', 'error');
            return;
        }

        const configuration_json = {
            columns: reportColumns.map(({ key, label, visible }) => ({ key, label, visible })),
            // Gelecekte sıralama ve filtre ayarları da buraya eklenebilir
        };

        const payload = {
            title: reportTitle,
            source_virtual_table_id: virtualTableId,
            configuration_json,
            sharing_status: 'PRIVATE', // Varsayılan
        };

        const { success } = await createReport(payload);
        if (success) {
            addNotification('Rapor başarıyla kaydedildi!', 'success');
            navigate('/nexus/reports'); // Raporlar galerisine yönlendir (bu sayfayı sonra yapacağız)
        } else {
            addNotification('Rapor kaydedilirken bir hata oluştu.', 'error');
        }
    };
    
    // --- Arayüz Çizimi ---
    if (sourceLoading) return <Spinner size="lg" />;
    if (sourceError) return <div className={styles.error}>Kaynak veri yüklenirken bir hata oluştu.</div>;

    const selectedColumn = reportColumns.find(c => c.key === selectedColumnKey) || null;

    return (
        <DndContext onDragEnd={handleDragEnd} collisionDetection={closestCenter}>
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
                    <AvailableColumns columns={sourceData?.columns || []} />
                    <ReportCanvas 
                        columns={reportColumns}
                        data={sourceData || {}}
                        onColumnClick={setSelectedColumnKey}
                        selectedColumnKey={selectedColumnKey}
                        setReportColumns={setReportColumns} // Yeniden sıralama için
                    />
                    <PropertiesPanel 
                        selectedColumn={selectedColumn}
                        onUpdateColumn={handleUpdateColumn}
                    />
                </div>
            </div>
        </DndContext>
    );
};

export default ReportPlayground;