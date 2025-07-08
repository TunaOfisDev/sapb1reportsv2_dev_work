// File: frontend/src/components/ProcureCompare/hooks/useProcureCompare.js

import { useState, useEffect, useCallback } from 'react';
import {
  fetchOrders,
  fetchQuotes,
  fetchComparisons,
  syncDataFromHana
} from '../api/procureCompareService';

/**
 * Satınalma Karşılaştırma verisini yönetmek için özel hook.
 */
const useProcureCompare = () => {
  const [orders, setOrders] = useState([]);
  const [quotes, setQuotes] = useState([]);
  const [comparisons, setComparisons] = useState([]);
  const [loading, setLoading] = useState(true);
  const [syncing, setSyncing] = useState(false);
  const [error, setError] = useState(null);
  const [syncSuccess, setSyncSuccess] = useState(false);
  const [lastSyncedAt, setLastSyncedAt] = useState(null); // Son güncelleme zamanı

  /**
   * Tüm verileri yükler
   */
  const loadAllData = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const [ordersData, quotesData, comparisonsResponse] = await Promise.all([
        fetchOrders(),
        fetchQuotes(),
        fetchComparisons()
      ]);

      const comparisonsData = Array.isArray(comparisonsResponse)
      ? comparisonsResponse
      : [];

      setOrders(Array.isArray(ordersData) ? ordersData : []);
      setQuotes(Array.isArray(quotesData) ? quotesData : []);
      setComparisons(comparisonsData);

      // comparisons içindeki en son created_at tarihini bul
      const latestCreated = comparisonsData.reduce((latest, item) => {
        const itemDate = new Date(item.created_at);
        return itemDate > latest ? itemDate : latest;
      }, new Date(0));

      setLastSyncedAt(latestCreated);

      console.log('Karşılaştırmalar geldi:', comparisonsData);
    } catch (err) {
      console.error('Veri yüklenirken hata:', err);
      setError(err);
    } finally {
      setLoading(false);
    }
  }, []);

  /**
   * HANA'dan veriyi senkronize eder
   */
  const handleSyncFromHana = useCallback(async () => {
    setSyncing(true);
    setSyncSuccess(false);
    setError(null);
    try {
      await syncDataFromHana();
      await loadAllData();
      setSyncSuccess(true);
    } catch (err) {
      console.error('HANA senkronizasyon hatası:', err);
      setError(err);
    } finally {
      setSyncing(false);
    }
  }, [loadAllData]);

  useEffect(() => {
    loadAllData();
  }, [loadAllData]);

  return {
    orders,
    quotes,
    comparisons,
    loading,
    syncing,
    error,
    syncSuccess,
    lastSyncedAt,
    reload: loadAllData,
    syncFromHana: handleSyncFromHana
  };
};

export default useProcureCompare;
