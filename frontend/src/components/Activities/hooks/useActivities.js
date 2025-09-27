// frontend/src/components/Activities/hooks/useActivities.js
import { useState, useEffect, useCallback } from 'react';
import activities from '../../../api/activities';
import exportToXLSX from '../utils/XLSXExport';

const useActivities = () => {
  const [localActivities, setLocalActivities] = useState([]);
  const [instantActivities, setInstantActivities] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [lastUpdated, setLastUpdated] = useState(null);

  const fetchLocalActivities = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const data = await activities.fetchLocalData();
      setLocalActivities(data);
      setLastUpdated(new Date());
    } catch (err) {
      setError(err);
    } finally {
      setIsLoading(false);
    }
  }, []);

  const fetchInstantActivities = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const data = await activities.fetchHanaData();
      setInstantActivities(data);
    } catch (err) {
      setError(err);
    } finally {
      setIsLoading(false);
    }
  }, []);

  const exportActivitiesToXLSX = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const response = await activities.exportActivitiesXLSX();
      exportToXLSX(response, 'activities.xlsx');
    } catch (err) {
      setError(err);
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchLocalActivities();
  }, [fetchLocalActivities]);

  return {
    localActivities,
    instantActivities,
    isLoading,
    error,
    fetchLocalActivities,
    fetchInstantActivities,
    exportActivitiesToXLSX,
    lastUpdated,
  };
};

export default useActivities;