// frontend/src/components/TunaInsTotalRisk/hooks/useTotalRisk.js
import { useState, useCallback, useEffect } from 'react';
import { fetchLocalData, fetchHanaData, getLastUpdatedTime, exportTotalRiskToXLSX } from '../../../api/tunainstotalrisk';

const useTotalRisk = () => {
  const [localData, setLocalData] = useState([]);
  const [hanaData, setHanaData] = useState([]);
  const [lastUpdated, setLastUpdated] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleFetchLocalData = useCallback(async () => {
    try {
      setLoading(true);
      const data = await fetchLocalData();
      setLocalData(data || []);
    } catch (err) {
      setError(err);
    } finally {
      setLoading(false);
    }
  }, []);

  const handleFetchHanaData = useCallback(async () => {
    try {
      setLoading(true);
      const data = await fetchHanaData();
      setHanaData(data || []);
    } catch (err) {
      setError(err);
    } finally {
      setLoading(false);
    }
  }, []);

  const handleFetchLastUpdatedTime = useCallback(async () => {
    try {
      setLoading(true);
      const lastUpdatedTime = await getLastUpdatedTime();
      setLastUpdated(lastUpdatedTime); // API'den dönen zaman bilgisini atayın
    } catch (err) {
      setError(err);
    } finally {
      setLoading(false);
    }
  }, []);

  const handleExportTotalRiskToXLSX = useCallback(async () => {
    setLoading(true);
    try {
      await exportTotalRiskToXLSX();
    } catch (err) {
      setError(err);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    handleFetchLocalData();
    handleFetchLastUpdatedTime();
  }, [handleFetchLocalData, handleFetchLastUpdatedTime]);

  return {
    localData,
    hanaData,
    lastUpdated,
    loading,
    error,
    fetchLocalData: handleFetchLocalData,
    fetchHanaData: handleFetchHanaData,
    fetchLastUpdatedTime: handleFetchLastUpdatedTime,
    exportTotalRiskToXLSX: handleExportTotalRiskToXLSX
  };
};

export default useTotalRisk;