// frontend/src/components/DynamicReport/hooks/useDynamicReport.js
import { useState, useEffect } from 'react';
import {
  getSqlTableList,
  fetchInstantData,
  createDynamicTable,
  getManualHeadersByTableName,
  getDynamicTableByTableName,
  testAndGenerateReport,
  getSqlQueryList
} from '../../../api/dynamicreport';

const useDynamicReport = (table_name) => {
  const [sqlQueryList, setSqlQueryList] = useState([]);
  const [sqlTableList, setSqlTableList] = useState([]);
  const [instantData, setInstantData] = useState([]);
  const [dynamicTable, setDynamicTable] = useState([]);
  const [manualHeaders, setManualHeaders] = useState([]);
  const [tableDetails, setTableDetails] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [shouldFetchData, setShouldFetchData] = useState(false);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setIsLoading(true);

        const fetchedSqlQueryList = await getSqlQueryList();
        Array.isArray(fetchedSqlQueryList)
          ? setSqlQueryList(fetchedSqlQueryList)
          : console.error('Beklenmeyen SQL sorgu yapısı:', fetchedSqlQueryList);

        const fetchedSqlTableList = await getSqlTableList();
        Array.isArray(fetchedSqlTableList)
          ? setSqlTableList(fetchedSqlTableList)
          : console.error('Beklenmeyen tablo listesi yapısı:', fetchedSqlTableList);

        if (shouldFetchData) {
          const fetchedInstantData = await fetchInstantData(table_name);
          const fetchedDynamicTable = await createDynamicTable(table_name);
          const fetchedManualHeaders = await getManualHeadersByTableName(table_name);
          const fetchedTableDetails = await getDynamicTableByTableName(table_name);

          setInstantData(fetchedInstantData);
          setDynamicTable(fetchedDynamicTable);
          setManualHeaders(fetchedManualHeaders);
          setTableDetails(fetchedTableDetails);

          setShouldFetchData(false);
        }

        if (!shouldFetchData && table_name) {
          const headers = await getManualHeadersByTableName(table_name);
          const details = await getDynamicTableByTableName(table_name);
          setManualHeaders(headers);
          setTableDetails(details);
        }

      } catch (error) {
        console.error('Bir hata oluştu:', error);
      } finally {
        setIsLoading(false);
      }
    };

    fetchData();
  }, [table_name, shouldFetchData]);

  const triggerFetchData = async () => {
    setIsLoading(true);
    try {
      await new Promise((resolve) => setTimeout(resolve, 3000));
      const headers = await getManualHeadersByTableName(table_name);
      const details = await getDynamicTableByTableName(table_name);

      if (headers.length === 0 || !details) {
        const data = await fetchInstantData(table_name);
        setInstantData(data);
      } else {
        setManualHeaders(headers);
        setTableDetails(details);
      }
    } catch (error) {
      console.error('Veri çekme hatası:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleGenerateReport = async (sqlQueryIds) => {
    setIsLoading(true);
    try {
      await testAndGenerateReport(sqlQueryIds);
      alert('SQL sorguları başarıyla çalıştırıldı ve rapor oluşturuldu.');
    } catch (error) {
      console.error('Rapor oluşturma hatası:', error);
      alert('Bir hata oluştu. Detaylar için konsolu kontrol edin.');
    } finally {
      setIsLoading(false);
    }
  };

  const prepareDataTable = () => {
    return tableDetails?.hana_data_set || [];
  };

  const dataTable = prepareDataTable();

  return {
    sqlQueryList,
    sqlTableList,
    instantData,
    dynamicTable,
    manualHeaders,
    tableDetails,
    dataTable,
    isLoading,
    setIsLoading,
    triggerFetchData,
    handleGenerateReport,
  };
};

export default useDynamicReport;
