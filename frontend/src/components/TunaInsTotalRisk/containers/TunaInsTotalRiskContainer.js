// frontend/src/components/TunaInsTotalRisk/containers/TotalRiskContainer.js
import React from 'react';
import useTotalRisk from '../hooks/useTotalRisk';
import TotalRiskTable from './TotalRiskTable';
import useAuth from '../../../auth/useAuth';
import { formatDateTime } from '../utils/DateTimeFormat';
import '../css/TotalRiskContainer.css';

const TunaInsTotalRiskContainer = () => {
  const { isAuthenticated } = useAuth();
  
  const {
    localData,
    hanaData,
    lastUpdated,
    loading,
    error,
    fetchLocalData,
    fetchHanaData,
    fetchLastUpdatedTime,
    exportTotalRiskToXLSX
  } = useTotalRisk();

  const formattedLastUpdated = formatDateTime(lastUpdated);

  const handleFetchLocalData = async () => {
    if (isAuthenticated) {
      await fetchLocalData();
    } else {
      console.log('Kullanıcı kimlik doğrulaması gerekli.');
    }
  };

  const handleFetchHanaData = async () => {
    if (isAuthenticated) {
      await fetchHanaData();
      await fetchLastUpdatedTime(); // HANA verisi çekildikten sonra güncellenme zamanını da çek
    } else {
      console.log('Kullanıcı kimlik doğrulaması gerekli.');
    }
  };

  const handleExportToXLSX = async () => {
    if (isAuthenticated) {
      await exportTotalRiskToXLSX();
    } else {
      console.log('Excel verisi indirmek için kullanıcı kimlik doğrulaması gerekli.');
    }
  };

  const combinedData = React.useMemo(() => [
    ...(Array.isArray(localData) ? localData : []),
    ...(Array.isArray(hanaData) ? hanaData : [])
  ], [localData, hanaData]);

  if (loading) return <div className="loading-message">Yükleniyor...</div>;
  if (error) return <div className="error-message">Hata: {error.message}</div>;

  if (!isAuthenticated) {
    return <div>Lütfen erişim için giriş yapın.</div>;
  }

  return (
    <div className="total-risk-container">
      <div className="total-risk-container__header">
        <h1 className="total-risk-container__title">
          Tuna Ins Musteri Bakiye Listesi
        </h1>
        {lastUpdated && (
          <p className="last-updated-time">Son Güncellenme: {formattedLastUpdated}</p>
        )}
        <div className="total-risk-container__actions">
          <button onClick={handleFetchLocalData} className="total-risk-container__button">
            Yerel Veri Çek
          </button>
          <button onClick={handleFetchHanaData} className="total-risk-container__button">
            HANA Anlık Veri Çek
          </button>
          <button onClick={handleExportToXLSX}  className="total-risk-container__button">
           Excel Aktar
          </button>
        </div>
      </div>
      <TotalRiskTable data={combinedData} />
    </div>
  );
};

export default TunaInsTotalRiskContainer;

