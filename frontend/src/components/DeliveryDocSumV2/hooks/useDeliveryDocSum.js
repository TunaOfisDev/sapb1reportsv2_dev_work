// frontend/src/components/DeliveryDocSumV2/hooks/useDeliveryDocSum.js
import { useState, useEffect, useCallback } from 'react';
import {
  fetchSummaryList,
  fetchHanaData,
  fetchDynamicNameColumns
} from '../../../api/deliverydocsumv2';

const useDeliveryDocSum = () => {
  /* --------------------------------------------------------------------- */
  /* STATE */
  /* --------------------------------------------------------------------- */
  const [data, setData] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [lastUpdated, setLastUpdated] = useState('');

  // Dinamik kolon adları (varsayılan Türkçe etiketler)
  const [columnNames, setColumnNames] = useState({
    today: 'Bugün',
    yesterday: 'Dün',
    dayBeforeYesterday: 'Önceki Gün',
    threeDaysAgo: 'Bugün - 3 Gün',
    fourDaysAgo: 'Bugün - 4 Gün',
    thisMonth: 'Bu Ay Toplam',
    lastMonth: 'Bu Ay - 1 Toplam',
    thisYear: 'Yıllık Toplam'
  });

  /* --------------------------------------------------------------------- */
  /* HELPERS */
  /* --------------------------------------------------------------------- */
  /** Yerel (PostgreSQL) veriyi yükle ve state’i güncelle */
  const loadLocalData = useCallback(async () => {
    setIsLoading(true);
    try {
      const localData = await fetchSummaryList();

      if (localData.length > 0) {
        setLastUpdated(localData[0].updated_at); // API’de 'updated_at' olduğunu varsayıyoruz
      }

      setData(localData);
      setError(null);
    } catch (err) {
      setError(err.message || 'Yerel veri alınırken hata oluştu.');
    } finally {
      setIsLoading(false);
    }
  }, []);

  /** Dinamik kolon etiketlerini çek */
  const loadDynamicNameColumns = useCallback(async () => {
    try {
      const response = await fetchDynamicNameColumns();
      setColumnNames(response);
    } catch (err) {
      setError(err.message || 'Dinamik kolon isimleri alınamadı.');
    }
  }, []);

  /** HANA’dan canlı veri çek, ardından yerel veriyi yeniden yükle */
  const fetchHana = useCallback(async () => {
    setIsLoading(true);
    try {
      // Sunucu OK döndürdüğü sürece 'başarılı' kabul ediyoruz
      await fetchHanaData();

      // Backend’de toplu INSERT bittiğinde yerel veriyi yenile
      setTimeout(loadLocalData, 2000); // İsterseniz süreyi ayarlayabilirsiniz
      setError(null);
    } catch (err) {
      console.error('HANA veri çekme hatası:', err);
      setError(err.message || 'HANA verisi alınırken hata oluştu.');
    } finally {
      // Butonu tekrar aktif etmek için (loadLocalData kendi isLoading’ini yönetecek)
      setIsLoading(false);
    }
  }, [loadLocalData]);

  /* --------------------------------------------------------------------- */
  /* EFFECTS */
  /* --------------------------------------------------------------------- */
  // İlk render’da yerel veriyi ve dinamik kolon adlarını çek
  useEffect(() => {
    loadLocalData();
    loadDynamicNameColumns();
  }, [loadLocalData, loadDynamicNameColumns]);

  /* --------------------------------------------------------------------- */
  /* PUBLIC API */
  /* --------------------------------------------------------------------- */
  return {
    data,
    isLoading,
    error,
    fetchHana,
    loadLocalData,
    columnNames,
    lastUpdated
  };
};

export default useDeliveryDocSum;
