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

// Yeni modüler bileşenlerimiz
import DetailBuilder from './DetailBuilder';
import PivotBuilder from './PivotBuilder';

const ReportPlayground = () => {
    const { virtualTableId } = useParams();
    const navigate = useNavigate();
    const { addNotification } = useNotifications();

    const { data: sourceData, loading: sourceLoading, error: sourceError, request: executeSourceQuery } = useApi(virtualTablesApi.executeVirtualTable);
    const { loading: isSaving, request: createReport } = useApi(reportTemplatesApi.createReportTemplate);

    const [reportTitle, setReportTitle] = useState('');
    const [reportType, setReportType] = useState('detail');
    const [configuration, setConfiguration] = useState({
        report_type: 'detail',
        columns: [],
        pivot_config: {},
    });

    const memoizedExecuteQuery = useCallback(executeSourceQuery, []);
    useEffect(() => {
        if (virtualTableId) {
            memoizedExecuteQuery(virtualTableId);
        }
    }, [virtualTableId, memoizedExecuteQuery]);

    const handleSave = async () => {
        if (!reportTitle) {
            addNotification('Lütfen rapora bir başlık verin.', 'error');
            return;
        }
        const payload = {
            title: reportTitle,
            source_virtual_table_id: virtualTableId,
            configuration_json: { ...configuration, report_type: reportType },
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
    if (sourceError) return <div className={styles.error}>Kaynak veri yüklenirken bir hata oluştu.</div>;

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
                    {isSaving ? 'Kaydediliyor...' : 'Raporu Kaydet'}
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
                    <PivotBuilder 
                        sourceColumns={sourceData?.columns || []}
                        onChange={(pivotConfig) => setConfiguration(prev => ({...prev, pivot_config: pivotConfig}))}
                    />
                )}
            </div>
        </div>
    );
};

export default ReportPlayground;