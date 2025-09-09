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
// YENİ: formatDynamicNumber fonksiyonunu import ediyoruz
import { formatDynamicNumber } from '../../utils/formatters';

/**
 * Bu bileşen, backend'den gelen "reportData" paketini ayrıştırır
 * ve rapor tipine göre uygun bileşeni render eder.
 */
const ReportResultRenderer = ({ reportData, loading, error }) => {
    if (loading) return <Spinner />;
    if (error) return <p style={{ color: 'red' }}>Rapor sonucu çalıştırılırken hata oluştu: {error}</p>;
    
    if (!reportData || !reportData.configuration || !reportData.data) {
       if (reportData?.data?.error) {
           return <p style={{ color: 'red' }}>Veri sorgulanırken hata oluştu: {reportData.data.error}</p>;
       }
       return <p>Rapor verisi alındı ancak formatı geçersiz.</p>;
    }

    const config = reportData.configuration;
    let data = reportData.data;
    const reportType = config?.report_type || 'detail';
    
    // ### YENİ MANTIK: SAYISAL VERİLERİ ÖNCE SAYIYA ÇEVİR, SONRA FORMATLA ###
    if (reportType === 'detail' && data && data.rows && data.columns) {
      // column_metadata'dan veri tipi bilgilerini al
      const columnMetadata = reportData.metadata;

      const formattedRows = data.rows.map(row => {
          const formattedRow = {};
          data.columns.forEach((col) => { // 'index' parametresini kaldırdık, çünkü kullanılmıyor
              const colName = col.accessor;
              const colMetadata = columnMetadata[colName] || {};
              const dataType = colMetadata.dataType;
              let value = row[col.accessor]; // col.id yerine col.accessor kullanıyoruz, çünkü Table bileşeni bu prop'u bekliyor

              if (dataType === 'number' && value !== null) {
                  const numberValue = Number(value);
                  if (!isNaN(numberValue)) {
                      value = formatDynamicNumber(numberValue);
                  }
              }
              // Buraya diğer veri tipleri için de formatlama eklenebilir (örn: 'date' ise formatDateTime)
              
              formattedRow[colName] = value;
          });
          return formattedRow;
      });

      // Table bileşeninin beklediği formatı koruyoruz
      const formattedData = {
          columns: data.columns,
          rows: formattedRows
      };

      return (
          <Table 
              data={formattedData} 
              loading={false}
              error={null}
          />
      );
    }

    if (reportType === 'pivot') {
        const pivotState = config?.pivot_config || { rows: [], columns: [], values: [] };
        
        return (
            <PivotRenderer 
                data={data} 
                pivotState={pivotState} 
            />
        );
    }

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

            {selectedReport && (
                <div className={styles.resultsContainer}>
                    <Card title={`Rapor Sonuçları: ${selectedReport.title}`}>
                        <ReportResultRenderer 
                            reportData={reportData} 
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