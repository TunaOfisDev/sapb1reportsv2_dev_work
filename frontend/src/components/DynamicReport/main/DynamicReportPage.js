// frontend/src/components/DynamicReport/main/DynamicReportPage.js
import React, { useState } from 'react';
import useDynamicReport from '../hooks/useDynamicReport';
import DynamicTable from './DynamicTable';
import ToastNotifications, { useToastNotifications } from '../utils/ToastNotifications';
import LoadingSpinner from '../utils/LoadingSpinner';
import exportToExcel from '../utils/DynamicXLSXExport';
import '../css/DynamicReportPage.css';

const DynamicReportPage = () => {
  const { addNotification } = useToastNotifications();
  const [selectedTableName, setSelectedTableName] = useState('');
  const {
    sqlTableList,
    dynamicTable,
    manualHeaders,
    tableDetails,
    isLoading,
    triggerFetchData,
  } = useDynamicReport(selectedTableName);

  const mergeDataWithHeaders = () => {
    if (manualHeaders.length === 0 || !tableDetails) {
      return dynamicTable;
    }

    const columns = manualHeaders.map((header) => header);
    const rows = tableDetails.hana_data_set.map((dataRow) => dataRow);

    return {
      columns,
      rows,
    };
  };

  const customizedTableData = mergeDataWithHeaders();

  const handleFetchData = async () => {
    try {
      triggerFetchData();
      addNotification('Veri çekme işlemi başlatıldı.', 'info');
      addNotification('Veriler başarıyla çekildi.', 'success');
    } catch (error) {
      addNotification('Veriler çekilemedi.', 'error');
    }
  };

  const exportToExcelWithHeaders = () => {
    const fileName = 'export_with_headers.xlsx';
    exportToExcel(customizedTableData.rows, fileName, manualHeaders);
  };

  return (
    <div className="dynamic-report-page">
      <div className="dynamic-report-page__controls">
        <div className="dynamic-report-page__sql-list">
          <h5 className="dynamic-report-page__label">SQL Tablo Listesi</h5>
          <select onChange={(e) => setSelectedTableName(e.target.value)} value={selectedTableName}>
            <option value="">Tablo Seçin</option>
            {sqlTableList.map((table, index) => (
              <option key={index} value={table}>
                {table}
              </option>
            ))}
          </select>
        </div>
        <button onClick={handleFetchData} className="dynamic-report-page__button">
          Dinamik Rapor Oluştur
        </button>
        <button onClick={exportToExcelWithHeaders} className="dynamic-report-page__button">
          Excel'e Aktar
        </button>
      </div>
      <LoadingSpinner isLoading={isLoading} className="dynamic-report-page__loading-spinner" />
      <DynamicTable data={customizedTableData} selectedTableName={selectedTableName} />
      <ToastNotifications />
    </div>
  );
};

export default DynamicReportPage;
