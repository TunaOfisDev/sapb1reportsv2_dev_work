// frontend/src/components/ProductGroupDeliverySum/hooks/useProductGroupDeliverySum.js
import { useState, useEffect, useMemo } from 'react';
import { 
  fetchLocalData, 
  fetchHanaData, 
  fetchYearComparisonData 
} from '../../../api/productgroupdeliverysum';

const useProductGroupDeliverySum = (initialYear = new Date().getFullYear()) => {
  // State yönetimi
  const [localData, setLocalData] = useState([]);
  const [hanaData, setHanaData] = useState([]);
  const [currentYearData, setCurrentYearData] = useState([]);
  const [previousYearData, setPreviousYearData] = useState([]);
  const [selectedYear, setSelectedYear] = useState(initialYear);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // İlk yüklemede local data'yı çekme
  useEffect(() => {
    const getLocalData = async () => {
      setLoading(true);
      try {
        const data = await fetchLocalData();
        setLocalData(data);
        setError(null);
      } catch (err) {
        setError('Yerel veriyi çekerken bir hata oluştu.');
      } finally {
        setLoading(false);
      }
    };

    getLocalData();
  }, []);

  // Seçili yıl değiştiğinde yıl karşılaştırma verilerini çekme
  useEffect(() => {
    const getYearComparisonData = async () => {
      setLoading(true);
      try {
        const data = await fetchYearComparisonData(selectedYear);
        setCurrentYearData(data.currentYear);
        setPreviousYearData(data.previousYear);
        setError(null);
      } catch (err) {
        setError('Yıl karşılaştırma verilerini çekerken bir hata oluştu.');
      } finally {
        setLoading(false);
      }
    };

    getYearComparisonData();
  }, [selectedYear]);

  // Yerel veri çekme işlemi
  const handleFetchLocalData = async () => {
    setLoading(true);
    try {
      const data = await fetchLocalData();
      setLocalData(data);
      setError(null);
    } catch (err) {
      setError('Yerel veriyi çekerken bir hata oluştu.');
    } finally {
      setLoading(false);
    }
  };

  // HANA'dan veri çekme işlemi
  const handleFetchHanaData = async () => {
  setLoading(true);
  try {
    const data = await fetchHanaData();
    setHanaData(data);
    setError(null);

    // 💡 HANA’dan veri geldikten sonra yıl karşılaştırma verilerini de güncelle
    const yearData = await fetchYearComparisonData(selectedYear);
    setCurrentYearData(yearData.currentYear);
    setPreviousYearData(yearData.previousYear);

  } catch (err) {
    setError('HANA verisini çekerken bir hata oluştu.');
  } finally {
    setLoading(false);
  }
};

  // Yıl değiştirme işlemi
  const handleYearChange = (year) => {
    setSelectedYear(year);
  };

  // Yıl karşılaştırma özet verileri
  const yearComparisonSummary = useMemo(() => {
    if (!currentYearData.length || !previousYearData.length) return null;

    const calculateTotal = (data) => data.reduce((sum, item) => sum + item.teslimat_tutar, 0);
    const currentTotal = calculateTotal(currentYearData);
    const previousTotal = calculateTotal(previousYearData);
    const percentageChange = ((currentTotal - previousTotal) / previousTotal) * 100;

    return {
      currentYearTotal: currentTotal,
      previousYearTotal: previousTotal,
      percentageChange: percentageChange,
      isIncrease: percentageChange > 0
    };
  }, [currentYearData, previousYearData]);

  return {
    // Mevcut veriler
    localData,
    hanaData,
    // Yıl karşılaştırma verileri
    currentYearData,
    previousYearData,
    yearComparisonSummary,
    selectedYear,
    // Durum bilgileri
    loading,
    error,
    // İşleyiciler
    handleFetchLocalData,
    handleFetchHanaData,
    handleYearChange
  };
};

export default useProductGroupDeliverySum;