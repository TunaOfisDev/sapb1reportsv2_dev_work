// frontend/src/components/RawMaterialWarehouseStock/hooks/useRawMaterialWarehouseStock.js
import { useState, useEffect, useCallback } from 'react';
import { 
  getRawMaterialWarehouseStocks, 
  fetchAndUpdateHanaData, 
  updateItemGroupSelection,
  updateZeroStockVisibility,
  getFilteredRawMaterialWarehouseStocks,
  exportColumnFilterData,
} from '../../../api/rawmaterialwarehousestock';
import { getTaskStatus } from '../../../api/celery';

const useRawMaterialWarehouseStock = () => {
  const [stocks, setStocks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [taskId, setTaskId] = useState(null);
  const [taskStatus, setTaskStatus] = useState(null);
  const [isHammaddeSelected, setIsHammaddeSelected] = useState(true);
  const [hideZeroStock, setHideZeroStock] = useState(true);
  const [selectedPurchaseOrders, setSelectedPurchaseOrders] = useState('');

  const fetchStocks = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      let data;
      if (isHammaddeSelected || hideZeroStock) {
        data = await getFilteredRawMaterialWarehouseStocks();
      } else {
        data = await getRawMaterialWarehouseStocks();
      }
      setStocks(data);
    } catch (error) {
      console.error('Error fetching raw material warehouse stocks:', error);
      setError(error);
    } finally {
      setLoading(false);
    }
  }, [isHammaddeSelected, hideZeroStock]);

  const fetchAndUpdateStocks = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const task = await fetchAndUpdateHanaData();
      setTaskId(task.task_id);
      setTaskStatus('PENDING');
    } catch (error) {
      console.error('Error starting fetch and update HANA data task:', error);
      setError(error);
      setLoading(false);
    }
  }, []);

  const checkTaskStatus = useCallback(async (taskId) => {
    try {
      const status = await getTaskStatus(taskId);
      setTaskStatus(status.state);
      if (status.state === 'SUCCESS') {
        await fetchStocks();
        setLoading(false);
      } else if (status.state === 'FAILURE') {
        setError('Task failed');
        setLoading(false);
      }
    } catch (error) {
      console.error('Error checking task status:', error);
      setError(error);
      setLoading(false);
    }
  }, [fetchStocks]);

  const handleSelectionChange = useCallback(async (isHammadde) => {
    try {
      await updateItemGroupSelection(isHammadde);
      setIsHammaddeSelected(isHammadde);
      await fetchStocks();
    } catch (error) {
      console.error('Seçim güncellenirken hata oluştu:', error);
      setError(error);
    }
  }, [fetchStocks]);

  const handleZeroStockVisibilityChange = useCallback(async (hideZeroStock) => {
    try {
      await updateZeroStockVisibility(hideZeroStock);
      setHideZeroStock(hideZeroStock);
      await fetchStocks();
    } catch (error) {
      console.error('Sıfır stok görünürlüğü güncellenirken hata oluştu:', error);
      setError(error);
    }
  }, [fetchStocks]);

  useEffect(() => {
    if (taskId && taskStatus === 'PENDING') {
      const interval = setInterval(() => checkTaskStatus(taskId), 1000);
      return () => clearInterval(interval);
    }
  }, [taskId, taskStatus, checkTaskStatus]);

  useEffect(() => {
    const initializeData = async () => {
      await updateItemGroupSelection(true);
      await updateZeroStockVisibility(true);
      await fetchStocks();
    };

    initializeData();
  }, [fetchStocks]);

  useEffect(() => {
    fetchAndUpdateStocks();
  }, [fetchAndUpdateStocks]);

  const setPurchaseOrders = useCallback((orders) => {
    setSelectedPurchaseOrders(orders);
  }, []);

  const handleExportFiltered = useCallback(async (columnFilters) => {
    try {
      const data = await exportColumnFilterData(columnFilters);
      const url = window.URL.createObjectURL(new Blob([data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', 'filtered_data.xlsx');
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (error) {
      console.error('Filtrelenmiş veri dışa aktarılırken hata oluştu:', error);
      setError(error);
    }
  }, []);

  return {
    data: stocks,
    loading,
    error,
    fetchStocks,
    fetchAndUpdateStocks,
    taskStatus,
    handleSelectionChange,
    isHammaddeSelected,
    hideZeroStock,
    handleZeroStockVisibilityChange,
    selectedPurchaseOrders,
    setPurchaseOrders,
    handleExportFiltered,       
  };
};

export default useRawMaterialWarehouseStock;
