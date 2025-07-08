// frontend/src/components/GirsbergerOrdrOpqt/hooks/useGirsbergerOrdrOpqt.js
import { useState, useEffect, useCallback } from 'react';
import { getOrdrDetailOpqt, fetchHanaData } from '../../../api/girsbergerordropqt';

const useGirsbergerOrdrOpqt = () => {
  const [data, setData] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [lastUpdated, setLastUpdated] = useState('');

  const loadLocalData = useCallback(async () => {
    console.log('loadLocalData called');  // Debugging amacıyla eklendi
    setIsLoading(true);
    try {
      const localData = await getOrdrDetailOpqt();
      console.log('Local data fetched', localData);  // Debugging amacıyla eklendi
      if (localData.length > 0) {
        setLastUpdated(localData[0].updated_at); // fetched data içinde updated_at olduğunu varsayıyorum
      }
      setData(localData);
      setError(null);
    } catch (err) {
      setError(err.message || 'Yerel verileri getirirken hata oluştu.');
    } finally {
      setIsLoading(false);
    }
  }, []);

  const fetchHana = useCallback(async () => {
    setIsLoading(true);
    try {
      const hanaResponse = await fetchHanaData();
      console.log('HANA response:', hanaResponse);
      if (hanaResponse.message === "HANA DB verileri başarıyla güncellendi ve cache temizlendi.") {
        console.log('HANA verileri başarıyla çekildi, yerel veritabanı güncelleniyor.');
        setTimeout(() => {
          console.log('HANA verileri çekildikten sonra yerel veriler yeniden yükleniyor...');
          loadLocalData().then(() => {
            setTimeout(() => {
              window.location.reload(); // Sayfayı yenile
            }, 1000); // Sayfanın yenilenmesi için kısa bir gecikme
          });
        }, 2000); // Backend işlem süresini ve yerel verilerin yenilenmesini simüle etmek için gecikme
      } else {
        console.error('HANA verilerini çekerken hata:', hanaResponse.message);
        setError(hanaResponse.message || 'HANA verilerini çekerken hata oluştu.');
      }
    } catch (err) {
      console.error('HANA verilerini çekerken istisna:', err);
      setError(err.message || 'HANA verilerini çekerken bir hata oluştu.');
    } finally {
      setIsLoading(false);
    }
  }, [loadLocalData]);

  useEffect(() => {
    loadLocalData();
  }, [loadLocalData]);

  return {
    data,
    isLoading,
    error,
    fetchHana,
    loadLocalData,
    lastUpdated 
  };
};

export default useGirsbergerOrdrOpqt;
