// File: frontend/src/components/ProcureCompare/hooks/useGroupedApprovalHistory.js

import { useEffect, useState } from 'react';
import { fetchGroupedApprovalHistory } from '../api/procureCompareService';

/**
 * Belge ve detay numarasına göre onay geçmişini getirir.
 *
 * @param {string} belgeNo - Belge numarası
 * @param {string} uniqDetailNo - Uniq detail numarası
 * @returns {{
 *   history: Array,
 *   loading: boolean,
 *   error: string | null
 * }}
 */
const useGroupedApprovalHistory = (belgeNo, uniqDetailNo) => {
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchHistory = async () => {
      if (!belgeNo || !uniqDetailNo) return;

      setLoading(true);
      setError(null);

      try {
        const result = await fetchGroupedApprovalHistory(belgeNo, uniqDetailNo);
        setHistory(result);
      } catch (err) {
        console.error('Onay geçmişi alınamadı:', err);
        setError('Onay geçmişi alınamadı');
      } finally {
        setLoading(false);
      }
    };

    fetchHistory();
  }, [belgeNo, uniqDetailNo]);

  return { history, loading, error };
};

export default useGroupedApprovalHistory;
