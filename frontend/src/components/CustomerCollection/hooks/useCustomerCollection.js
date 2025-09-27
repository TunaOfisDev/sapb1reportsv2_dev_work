// frontend/src/components/CustomerCollection/hooks/useCustomerCollection.js
import { useState, useEffect, useCallback } from 'react';
import customerCollectionApi from '../../../api/customercollection';
import XLSXExport from '../utils/XLSXExport';

const useCustomerCollection = () => {
  const [localDbCustomerCollections, setLocalDbCustomerCollections] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [lastUpdated, setLastUpdated] = useState(null);

  /* --- Yerel veriyi getir --- */
  const fetchLocalDbCustomerCollections = useCallback(async () => {
    setLoading(true);
    try {
      const response = await customerCollectionApi.getLocalDbCustomerCollections();
      setLocalDbCustomerCollections(response);
    } catch (err) {
      setError(err);
    } finally {
      setLoading(false);
    }
  }, []);

  /* --- HANA’dan anlık veri çek ve tabloyu anında güncelle --- */
  const fetchHanaDbCustomerCollection = useCallback(async () => {
    setLoading(true);
    try {
      const response = await customerCollectionApi.fetchHanaDbCustomerCollection();
      /* API HANA’dan veriyi döndürüyorsa doğrudan tabloya yazıyoruz */
      setLocalDbCustomerCollections(response);
      /* İsterseniz backend’de tutulan zaman yerine hemen şimdi damga basabilirsiniz: */
      setLastUpdated(new Date().toLocaleString('tr-TR'));
    } catch (err) {
      setError(err);
    } finally {
      setLoading(false);
    }
  }, []);

  /* --- Son güncelleme bilgisini getir --- */
  const fetchLastUpdatedCustomerCollection = useCallback(async () => {
    setLoading(true);
    try {
      const lastUpdatedTime = await customerCollectionApi.getLastUpdatedCustomerCollection();
      setLastUpdated(lastUpdatedTime);
    } catch (err) {
      setError(err);
    } finally {
      setLoading(false);
    }
  }, []);

  /* --- Excel Export --- */
  const exportCustomerCollectionsToXLSX = () => {
    XLSXExport.exportToExcel(localDbCustomerCollections, 'Musteri_Koleksiyonlari');
  };

  /* Sayfa ilk açıldığında yerel veri + zaman damgası getir */
  useEffect(() => {
    fetchLocalDbCustomerCollections();
    fetchLastUpdatedCustomerCollection();
  }, [fetchLocalDbCustomerCollections, fetchLastUpdatedCustomerCollection]);

  return {
    localDbCustomerCollections,
    lastUpdated,
    loading,
    error,
    fetchLocalDbCustomerCollections,
    fetchHanaDbCustomerCollection,
    fetchLastUpdatedCustomerCollection,
    exportCustomerCollectionsToXLSX,
  };
};

export default useCustomerCollection;

