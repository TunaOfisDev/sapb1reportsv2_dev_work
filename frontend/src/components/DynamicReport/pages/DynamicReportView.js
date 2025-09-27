// frontend/src/components/DynamicReport/pages/DynamicReportView.js
import { useParams } from 'react-router-dom';
import useDynamicReport from '../hooks/useDynamicReport';
import DynamicTable from '../main/DynamicTable';
import LoadingSpinner from '../utils/LoadingSpinner';
import { useEffect } from 'react';

const DynamicReportView = () => {
  const { table_name } = useParams();
  const {
    dataTable,
    manualHeaders,
    isLoading,
    tableDetails
  } = useDynamicReport(table_name);

  useEffect(() => {
    console.log('▶︎ Route parametresi (table_name):', table_name);
    console.log('▶︎ tableDetails:', tableDetails);
    console.log('▶︎ manualHeaders:', manualHeaders);
    console.log('▶︎ dataTable:', dataTable);
    if (tableDetails && tableDetails.hana_data_set) {
      console.log('▶︎ HANA data set örnek satır:', tableDetails.hana_data_set[0]);
    }
  }, [table_name, tableDetails, manualHeaders, dataTable]);

  if (isLoading || !tableDetails) {
    return <LoadingSpinner message="Rapor yükleniyor..." />;
  }

  if (!dataTable || dataTable.length === 0 || manualHeaders.length === 0) {
    return <div>Veri bulunamadı.</div>;
  }

  const tablePayload = {
    columns: manualHeaders,
    rows: dataTable
  };

  return (
    <div className="p-4">
      <h1 className="text-xl font-semibold mb-4">Rapor: {table_name}</h1>
      <DynamicTable data={tablePayload} selectedTableName={table_name} />
    </div>
  );
};

export default DynamicReportView;
