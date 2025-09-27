// frontend/src/components/DynamicReport/containers/DynamicReportContainer.js
import React from 'react';
import '../css/DynamicReportContainer.css';
import useDynamicReport from '../hooks/useDynamicReport'; 

const DynamicReportPage = React.lazy(() => import('../main/DynamicReportPage'));

const DynamicReportContainer = ({ manualHeaders, selectedTableName, triggerFetchData }) => {
  const { handleGenerateReport, sqlQueryList, isLoading } = useDynamicReport(selectedTableName);

  const handleGenerateReportClick = () => {
    const sqlQueryIds = sqlQueryList.map(query => query.id);
    handleGenerateReport(sqlQueryIds);
  };

  return (
    <div className="dynamic-report-container">
      <h1 className="dynamic-report-container__header">Dynamic Reports</h1>
      {isLoading ? (
        <div>Yükleniyor...</div>
      ) : (
        <>
          <button onClick={handleGenerateReportClick} className="dynamic-report-container__button">
            Seçilen SQL sorguyu test et ve verileri olustur/guncelle
          </button>
          <select>
            {sqlQueryList.length > 0 && sqlQueryList.map((query) => (
              <option key={query.id} value={query.id}>{query.table_name}</option>
            ))}
          </select>
          <React.Suspense fallback={<div>Yükleniyor...</div>}>
            <DynamicReportPage 
              table_name={selectedTableName} 
              manualHeaders={manualHeaders} 
              selectedTableName={selectedTableName} 
              triggerFetchData={triggerFetchData}
            />
          </React.Suspense>
        </>
      )}
    </div>
  );
};

export default DynamicReportContainer;
