// File: frontend/src/components/ProcureCompare/hooks/useItemPurchaseHistory.js

import { useState, useCallback } from 'react';
import { fetchItemPurchaseHistory } from '../api/procureCompareService';

export const useItemPurchaseHistory = () => {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [source, setSource] = useState(null);

  const loadItemPurchaseHistory = useCallback(async (itemCode) => {
    if (!itemCode) return;

    setLoading(true);
    setError(null);

    try {
      const result = await fetchItemPurchaseHistory(itemCode);

      if (result && Array.isArray(result.records)) {
        const { source, records } = result;

        const transformedData = records.map((item, index) => ({
          key: item.BelgeNo ?? index, // ✅ Kararlı key
          ItemCode: item.ItemCode,
          Tarih: item.Tarih,
          BelgeNo: item.BelgeNo,
          TedarikciKodu: item.TedarikciKodu,
          TedarikciAdi: item.TedarikciAdi,
          Miktar: item.Miktar,
          NetFiyat_Doviz: item.NetFiyat_Doviz,
          Doviz: item.Doviz,
          Kur: item.Kur,
          ToplamTutar_Doviz: item.ToplamTutar_Doviz,
          NetFiyat_YPB: item.NetFiyat_YPB,
          ToplamTutar_YPB: item.ToplamTutar_YPB
        }));

        setData(transformedData);
        setSource(source);
      } else {
        setData([]);
        setSource(null);
      }
    } catch (err) {
      console.error('useItemPurchaseHistory hook hata:', err);
      setError(err);
      setData([]);
      setSource(null);
    } finally {
      setLoading(false);
    }
  }, []);

  return {
    data,
    loading,
    error,
    source,
    loadItemPurchaseHistory
  };
};

