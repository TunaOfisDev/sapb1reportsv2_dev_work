// path: frontend/src/components/NexusCore/containers/ReportViewer/index.jsx

import React, { useState, useEffect, useMemo } from 'react';
import { useNavigate } from 'react-router-dom';
import { useTable } from 'react-table';
import styles from './ReportViewer.module.scss';

// ... (diğer importlar aynı kalıyor) ...
import ReportList from './ReportList';
import Card from '../../components/common/Card/Card';
import Spinner from '../../components/common/Spinner/Spinner';
import { formatCell } from '../../utils/formatters';
import { useReportTemplates } from '../../hooks/useReportTemplatesApi';
import { useApi } from '../../hooks/useApi';
import * as reportTemplatesApi from '../../api/reportTemplatesApi';

/**
 * Gelen veri ve meta veriyi kullanarak akıllı, formatlanmış
 * ve sıralanabilir bir tablo oluşturan bileşen.
 */
const SmartTable = ({ data, metadata }) => {
    // 1. ADIM: Kolon tanımlarını meta veriden oluşturuyoruz (Bu kısım zaten doğruydu).
    const columns = useMemo(() => {
        if (!data?.columns || !metadata) {
            return [];
        }
        return data.columns.map(colName => {
            const colMeta = metadata[colName] || {};
            const dataType = colMeta.dataType || 'string';
            const isNumeric = ['integer', 'decimal', 'number'].includes(dataType);
            
            return {
                Header: colMeta.label || colName,
                accessor: colName,
                Cell: ({ cell: { value } }) => formatCell(value, dataType),
                className: isNumeric ? styles.textRight : styles.textLeft,
            };
        });
    }, [data.columns, metadata]);

    // 2. ADIM (YENİ): Backend'den gelen [dizi, dizi] formatını [obje, obje] formatına dönüştürüyoruz.
    const memoizedData = useMemo(() => {
        if (!data?.rows || !data?.columns) {
            return [];
        }
        const columnKeys = data.columns;
        return data.rows.map(rowArray => {
            const rowObject = {};
            columnKeys.forEach((key, index) => {
                rowObject[key] = rowArray[index];
            });
            return rowObject;
        });
    }, [data.rows, data.columns]);

    // 3. ADIM (DÜZELTME): useTable kancasına artık doğru formatlanmış veriyi veriyoruz.
    const { 
        getTableProps, 
        getTableBodyProps, 
        headerGroups, 
        rows, 
        prepareRow 
    } = useTable({ columns, data: memoizedData });

    // Render kısmı aynı kalıyor, çünkü artık her şey doğru çalışacak.
    return (
        <div className={styles.tableContainer}>
            <table {...getTableProps()} className={styles.smartTable}>
                <thead>
                    {headerGroups.map(headerGroup => (
                        <tr {...headerGroup.getHeaderGroupProps()}>
                            {headerGroup.headers.map(column => (
                                <th {...column.getHeaderProps({ className: column.className })}>
                                    {column.render('Header')}
                                </th>
                            ))}
                        </tr>
                    ))}
                </thead>
                <tbody {...getTableBodyProps()}>
                    {rows.map(row => {
                        prepareRow(row);
                        return (
                            <tr {...row.getRowProps()}>
                                {row.cells.map(cell => (
                                    <td {...cell.getCellProps({ className: cell.column.className })}>
                                        {cell.render('Cell')}
                                    </td>
                                ))}
                            </tr>
                        );
                    })}
                </tbody>
            </table>
        </div>
    );
};


// ReportResultRenderer ve ReportViewer bileşenleri aynı kalabilir,
// çünkü sorun SmartTable'ın içindeydi.
const ReportResultRenderer = ({ reportData, loading, error }) => {
    // ... (Bu bileşende değişiklik yok) ...
    if (loading) return <Spinner />;
    if (error) return <p className={styles.errorMessage}>Rapor çalıştırılırken hata: {error.message || 'Bilinmeyen bir hata oluştu.'}</p>;
    if (!reportData || !reportData.success) {
        return <p className={styles.errorMessage}>Rapor verisi alınamadı: {reportData?.error || 'Geçersiz yanıt.'}</p>;
    }
    return <SmartTable data={{ columns: reportData.columns, rows: reportData.rows }} metadata={reportData.metadata} />;
};

const ReportViewer = () => {
    // ... (Bu bileşende değişiklik yok) ...
    const navigate = useNavigate();
    const { templates, isLoading: listLoading, error: listError, loadTemplates, deleteTemplate } = useReportTemplates();
    const { data: reportData, loading: executeLoading, error: executeError, request: executeReport } = useApi(reportTemplatesApi.executeReportTemplate);
    const [selectedReport, setSelectedReport] = useState(null);

    useEffect(() => { loadTemplates(); }, [loadTemplates]);

    const handleExecute = (report) => {
        setSelectedReport(report); 
        executeReport(report.id);
    };

    const handleDelete = async (reportId) => {
        const { success } = await deleteTemplate(reportId);
        if (success && selectedReport && selectedReport.id === reportId) {
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
            {listError && <p className={styles.errorMessage}>Rapor listesi yüklenirken hata oluştu.</p>}

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