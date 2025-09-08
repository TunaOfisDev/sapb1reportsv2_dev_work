// path: frontend/src/components/NexusCore/containers/ReportPlayground/index.jsx

import React, { useState, useEffect, useCallback } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import styles from './ReportPlayground.module.scss';

// Hook'lar, API'ler ve Ortak Bileşenler
import { useApi } from '../../hooks/useApi';
import { useNotifications } from '../../hooks/useNotifications';
import * as virtualTablesApi from '../../api/virtualTablesApi';
import * as reportTemplatesApi from '../../api/reportTemplatesApi';
import Spinner from '../../components/common/Spinner/Spinner';
import Button from '../../components/common/Button/Button';
import Input from '../../components/common/Input/Input';

// Modüler bileşenlerimiz
import DetailBuilder from './DetailBuilder';
import PivotBuilder from './PivotBuilder';

// Boş bir konfigürasyon şablonu
const EMPTY_CONFIG = {
    report_type: 'detail',
    columns: [],
    pivot_config: { rows: [], columns: [], values: [], filters: [] },
};

const ReportPlayground = () => {
    // 1. Mod Tespiti ve Hook Tanımlamaları
    const { virtualTableId, reportId } = useParams();
    const isEditMode = Boolean(reportId); 

    const navigate = useNavigate();
    const { addNotification } = useNotifications();

    // 2. API Kancaları
    const { data: sourceData, loading: sourceLoading, error: sourceError, request: executeSourceQuery } = useApi(virtualTablesApi.executeVirtualTable);
    const { data: existingTemplate, loading: templateLoading, request: getTemplate } = useApi(reportTemplatesApi.getReportTemplateById);
    const { loading: isSaving, request: saveReportApi } = useApi(
        isEditMode ? reportTemplatesApi.updateReportTemplate : reportTemplatesApi.createReportTemplate
    );

    // 3. State Yönetimi
    const [reportTitle, setReportTitle] = useState('');
    const [reportType, setReportType] = useState('detail');
    const [configuration, setConfiguration] = useState(EMPTY_CONFIG);
    const [currentSourceTableId, setCurrentSourceTableId] = useState(virtualTableId || null);


    // 4. Veri Yükleme Mantığı (SONSUZ DÖNGÜ DÜZELTMESİ)
    useEffect(() => {
        // Bu efektin niyeti SADECE route parametreleri değiştiğinde çalışmaktır.
        // getTemplate, addNotification, navigate gibi hook'lardan dönen fonksiyonlar
        // her render'da yeniden oluşur ve bağımlılık dizisinde olurlarsa sonsuz döngü yaratırlar.
        
        if (isEditMode && reportId) {
            const fetchTemplate = async () => {
                const { success, data } = await getTemplate(reportId); // Fonksiyonu doğrudan kullan
                if (success) {
                    setReportTitle(data.title);
                    const config = data.configuration_json || EMPTY_CONFIG;
                    setConfiguration(config);
                    setReportType(config.report_type || 'detail');
                    setCurrentSourceTableId(data.source_virtual_table);
                } else {
                    addNotification('Mevcut rapor yüklenirken hata oluştu.', 'error');
                    navigate('/nexus/reports'); 
                }
            };
            fetchTemplate();
        } else if (virtualTableId) {
            setCurrentSourceTableId(virtualTableId);
        }
    
    // Bağımlılık dizisinden kararsız fonksiyonları kasıtlı olarak çıkarıyoruz.
    // Bu efekt SADECE ID'ler değiştiğinde çalışacak, fonksiyon referansları değiştiğinde değil.
    // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [isEditMode, reportId, virtualTableId]); 


    // Kaynak Veri Yükleyici (Bu kanca, memoize edilmiş bir fonksiyona bağlı olmalı)
    const memoizedExecuteQuery = useCallback(executeSourceQuery, [executeSourceQuery]);
    useEffect(() => {
        if (currentSourceTableId) {
            memoizedExecuteQuery(currentSourceTableId);
        }
    }, [currentSourceTableId, memoizedExecuteQuery]);

    
    // Pivot Döngü Kırıcı (Bu düzeltme geçerliliğini koruyor)
    const handlePivotChange = useCallback((pivotConfig) => {
        setConfiguration(prev => ({ ...prev, pivot_config: pivotConfig }));
    }, []); 

    // 5. Akıllı Kaydetme Fonksiyonu
    const handleSave = async () => {
        if (!reportTitle) {
            addNotification('Lütfen rapora bir başlık verin.', 'error');
            return;
        }
        const payload = {
            title: reportTitle,
            source_virtual_table_id: currentSourceTableId,
            configuration_json: { ...configuration, report_type: reportType },
            sharing_status: existingTemplate?.sharing_status || 'PRIVATE',
        };

        const { success } = await (isEditMode ? saveReportApi(reportId, payload) : saveReportApi(payload));

        if (success) {
            addNotification(`Rapor başarıyla ${isEditMode ? 'güncellendi' : 'kaydedildi'}!`, 'success');
            navigate('/nexus/reports');
        } else {
            addNotification('Rapor kaydedilirken bir hata oluştu.', 'error');
        }
    };

    // ... (Render bloğu aynı) ...
    if (sourceLoading || templateLoading) return <Spinner size="lg" />;
    if (sourceError) return <div className={styles.error}>Kaynak veri yüklenirken bir hata oluştu.</div>;
    const sourceColumns = sourceData?.columns || [];

    return (
        <div className={styles.pageContainer}>
            <header className={styles.pageHeader}>
                <Input 
                    id="report-title"
                    label="Rapor Başlığı"
                    value={reportTitle} 
                    onChange={(e) => setReportTitle(e.target.value)}
                    placeholder="Örn: Aylık Müşteri Risk Analizi"
                />
                <div className={styles.modeSwitcher}>
                    <button className={`${styles.modeButton} ${reportType === 'detail' ? styles.active : ''}`} onClick={() => setReportType('detail')}>
                        Detay Tablo
                    </button>
                    <button className={`${styles.modeButton} ${reportType === 'pivot' ? styles.active : ''}`} onClick={() => setReportType('pivot')}>
                        Özet (Pivot) Tablo
                    </button>
                </div>
                <Button onClick={handleSave} variant="primary" disabled={isSaving}>
                    {isSaving ? 'Kaydediliyor...' : (isEditMode ? 'Raporu Güncelle' : 'Raporu Kaydet')}
                </Button>
            </header>
            
            <div className={styles.playgroundContainer}>
                {reportType === 'detail' ? (
                    <DetailBuilder 
                        sourceData={sourceData}
                        config={configuration}
                        setConfig={setConfiguration}
                    />
                ) : (
                    sourceColumns.length > 0 && (
                        <PivotBuilder 
                            sourceColumns={sourceColumns}
                            initialConfig={configuration.pivot_config || {}}
                            onChange={handlePivotChange} 
                        />
                    )
                )}
            </div>
        </div>
    );
};

export default ReportPlayground;