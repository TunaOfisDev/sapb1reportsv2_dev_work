// frontend/src/components/GirsbergerOrdrOpqt/containers/GirsbergerOrdrOpqtContainer.js
import React, { useEffect } from 'react';
import useGirsbergerOrdrOpqt from '../hooks/useGirsbergerOrdrOpqt';
import GirsbergerOrdrOpqtTable from './GirsbergerOrdrOpqtTable';
import XLSXExport from '../utils/XLSXExport';
import formatDateTime from '../utils/DateTimeFormat';
import '../css/GirsbergerOrdrOpqtContainer.css';

class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true };
  }

  componentDidCatch(error, errorInfo) {
    console.error('Caught an error:', error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return <h1>Bir şeyler yanlış gitti.</h1>;
    }
    return this.props.children;
  }
}

const GirsbergerOrdrOpqtContainer = () => {
  const {
    lastUpdated,
    loading,
    error,
    data,
    fetchHana,
    loadLocalData,
  } = useGirsbergerOrdrOpqt();

  useEffect(() => {
    loadLocalData();
  }, [loadLocalData]);

  const handleExport = () => {
    console.log('Exporting to Excel', data);
    XLSXExport.exportToExcel(data, 'girsberger_ordr_opqt_report');
  };

  const handleLoadLocalData = () => {
    console.log('Yerel veri çek butonuna basıldı');
    loadLocalData().then(() => {
      setTimeout(() => {
        window.location.reload(); // Sayfayı yenile
      }, 1000); // Sayfanın yenilenmesi için kısa bir gecikme
    });
  };

  const handleFetchHana = () => {
    console.log('HANA anlık veri çek butonuna basıldı');
    fetchHana();
  };

  return (
    <ErrorBoundary>
      <div className="girsberger-ordr-opqt-container">
        <div className="girsberger-ordr-opqt-container__header">
          <h3 className="girsberger-ordr-opqt-container__title">
            Girsberger Satis Siparis to Satinalma Teklif
          </h3>

          <div className="girsberger-ordr-opqt-container__last-updated">
            {lastUpdated ? `Son Güncellenme: ${formatDateTime(lastUpdated)}` : ''}
          </div>

          <div className="girsberger-ordr-opqt-container__button-wrapper">
            <button onClick={handleLoadLocalData} className="girsberger-ordr-opqt-container__button" disabled={loading}>
              Yerel Veri Çek
            </button>
            <button onClick={handleFetchHana} className="girsberger-ordr-opqt-container__button" disabled={loading}>
              HANA Anlık Veri Çek
            </button>
            <button onClick={handleExport} className="girsberger-ordr-opqt-container__button" disabled={loading}>
              Excel'e Aktar
            </button>
          </div>
        </div>
        {loading ? (
          <div className="loading-message">Yükleniyor...</div>
        ) : error ? (
          <div className="error-message">Veri yükleme hatası: {error.message}</div>
        ) : (
          <GirsbergerOrdrOpqtTable data={data} />
        )}
      </div>
    </ErrorBoundary>
  );
};

export default GirsbergerOrdrOpqtContainer;
