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

const ReportViewer = () => {
    const navigate = useNavigate();

    // Rapor şablonlarının CRUD işlemleri için özel hook'umuzu kullanıyoruz.
    const { templates, isLoading: listLoading, error: listError, loadTemplates, deleteTemplate } = useReportTemplates();
    
    // Tek bir raporu çalıştırmak için jenerik useApi hook'unu kullanıyoruz.
    const { data: reportData, loading: executeLoading, error: executeError, request: executeReport } = useApi(reportTemplatesApi.executeReportTemplate);

    const [selectedReport, setSelectedReport] = useState(null);

    // Bileşen ilk yüklendiğinde rapor listesini çek.
    useEffect(() => {
        loadTemplates();
    }, [loadTemplates]);

    // Olay Yöneticileri
    const handleExecute = (report) => {
        setSelectedReport(report);
        executeReport(report.id);
    };

    const handleDelete = async (report) => {
        const { success } = await deleteTemplate(report.id);
        if (success && selectedReport && selectedReport.id === report.id) {
            setSelectedReport(null); // Eğer gösterilen rapor silindiyse, sonuçları temizle
        }
    };
    
    const handleEdit = (report) => {
        // Kullanıcıyı, raporun kaynak sorgusunun ID'si ile Playground'a yönlendir.
        navigate(`/nexus/playground/${report.source_virtual_table}`);
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

            {selectedReport && (
                <div className={styles.resultsContainer}>
                    <Card title={`Rapor Sonuçları: ${selectedReport.title}`}>
                        <Table 
                            data={reportData}
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