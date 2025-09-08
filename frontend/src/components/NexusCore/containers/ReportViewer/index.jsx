// path: frontend/src/components/NexusCore/containers/ReportViewer/index.jsx
import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import styles from './ReportViewer.module.scss';

// Hook'lar ve API'ler
import { useReportTemplates } from '../../hooks/useReportTemplatesApi';
import { useApi } from '../../hooks/useApi';
import * as reportTemplatesApi from '../../api/reportTemplatesApi';

// Bileşenler
import ReportList from './ReportList';
import Card from '../../components/common/Card/Card';
import Table from '../../components/common/Table/Table';
import Spinner from '../../components/common/Spinner/Spinner';
import PivotRenderer from '../ReportPlayground/PivotBuilder/PivotRenderer';


/**
 * ### MİMARİ DÜZELTME ###
 * Bu bileşen artık "reportData" adında TEK BİR nesne alıyor.
 * Bu nesne, API'den dönen { configuration: {...}, data: {...} } paketinin tamamıdır.
 * Bu bileşen, bu paketi AÇMAKTAN sorumludur.
 */
const ReportResultRenderer = ({ reportData, loading, error }) => {
    if (loading) return <Spinner />;
    // Backend hatasını doğrudan göster
    if (error) return <p style={{ color: 'red' }}>Rapor sonucu çalıştırılırken hata oluştu: {error}</p>;
    
    // API çağrısı başarılı olduysa AMA data boşsa (veya paket formatı yanlışsa)
    if (!reportData || !reportData.configuration || !reportData.data) {
         // Eğer reportData.data'nın içinde kendi 'error'u varsa onu göster (örn: SQL hatası)
         if (reportData?.data?.error) {
            return <p style={{ color: 'red' }}>Veri sorgulanırken hata oluştu: {reportData.data.error}</p>;
         }
         // Beklenmedik bir cevap formatı
         return <p>Rapor verisi alındı ancak formatı geçersiz.</p>;
    }

    // ### PAKETİ AÇIYORUZ ###
    const config = reportData.configuration;
    const data = reportData.data; // Bu bizim { columns: [...], rows: [...] } nesnemiz
    
    const reportType = config?.report_type || 'detail';

    if (reportType === 'pivot') {
        // Pivot motoruna ham veri (data) ve pivot planını (config.pivot_config) veriyoruz.
        const pivotState = config?.pivot_config || { rows: [], columns: [], values: [] };
        
        return (
            <PivotRenderer 
                data={data} 
                pivotState={pivotState} 
            />
        );
    }

    // Rapor 'detail' ise, standart düz tabloya ham datayı (veya filtrelenmiş datayı, 
    // backend ne döndürdüyse) veriyoruz.
    return (
        <Table 
            data={data} 
            loading={false}
            error={null}
        />
    );
};


const ReportViewer = () => {
    const navigate = useNavigate();
    const { templates, isLoading: listLoading, error: listError, loadTemplates, deleteTemplate } = useReportTemplates();
    
    // 'reportData' artık bizim BÜYÜK PAKETİMİZİ ({ config, data }) tutuyor
    const { data: reportData, loading: executeLoading, error: executeError, request: executeReport } = useApi(reportTemplatesApi.executeReportTemplate);

    const [selectedReport, setSelectedReport] = useState(null);

    useEffect(() => {
        loadTemplates();
    }, [loadTemplates]);

    const handleExecute = (report) => {
        setSelectedReport(report); 
        executeReport(report.id);
    };

    const handleDelete = async (report) => {
        // ... (Bu fonksiyon aynı, değişiklik yok) ...
        const { success } = await deleteTemplate(report.id);
        if (success && selectedReport && selectedReport.id === report.id) {
            setSelectedReport(null); 
        }
    };
    
    const handleEdit = (report) => {
        navigate(`/nexus/playground/edit/${report.id}`);
    };

    return (
        <div className={styles.viewerContainer}>
            <header className={styles.header}>
                <h1>Rapor Galerisi</h1>
            </header>

            {listLoading ? <Spinner /> : 
                <ReportList 
                    reports={templates}
                    onExecute={handleExecute}
                    onEdit={handleEdit}
                    onDelete={handleDelete}
                />
            }
            {listError && <p style={{color: 'red'}}>Rapor listesi yüklenirken bir hata oluştu.</p>}

            {/* Sonuç Alanı */}
            {selectedReport && (
                <div className={styles.resultsContainer}>
                    <Card title={`Rapor Sonuçları: ${selectedReport.title}`}>
                        {/* ### NİHAİ DÜZELTME ###
                          Akıllı Renderer'a artık sadece API'den dönen BÜYÜK PAKETİ yolluyoruz.
                          Artık 'selectedReport.configuration_json'a (güvenilmez olana) ihtiyacımız yok.
                        */}
                        <ReportResultRenderer 
                            reportData={reportData} // { config, data } paketinin tamamı
                            loading={executeLoading}
                            error={executeError}
                        />
                    </Card>
                </div>
            )}
        </div>
    );
};

export default ReportViewer;