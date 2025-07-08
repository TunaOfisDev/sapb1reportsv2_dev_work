// path: frontend/src/components/StockCardIntegration/hooks/useHelpTexts.js

import { useEffect, useState } from 'react';
import { fetchFieldHelpTexts } from '../api/stockCardApi';

/**
 * Dinamik alan açıklamaları için hook
 * - API'den helptext kayıtlarını çeker.
 * - Alan adına göre filtreleme fonksiyonu sunar.
 */
const useHelpTexts = () => {
  const [helpTexts, setHelpTexts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const loadHelpTexts = async () => {
      try {
        const data = await fetchFieldHelpTexts();
        setHelpTexts(data);
      } catch (err) {
        setError('Alan açıklamaları alınamadı.');
      } finally {
        setLoading(false);
      }
    };

    loadHelpTexts();
  }, []);

  /**
   * Belirli bir field_name için açıklama getir
   * @param {string} fieldName 
   * @returns {object|null}
   */
  const getHelpTextByField = (fieldName) => {
    return helpTexts.find((item) => item.field_name === fieldName) || null;
  };

  return { helpTexts, getHelpTextByField, loading, error };
};

export default useHelpTexts;
