// frontend/src/components/OpenOrderDocSum/containers/OpenOrderDocSumContainer.js
import React, { useEffect } from 'react';
import useOpenOrderDocSum from '../hooks/useOpenOrderDocSum';
import OpenOrderDocSumTable from './OpenOrderDocSumTable';
import XLSXExport from '../utils/XLSXExport'; // XLSXExport modülünü import edin
import '../css/OpenOrderDocSumContainer.css';

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

const OpenOrderDocSumContainer = () => {
  const {
    lastUpdated,
    loading,
    error,
    documentSummaries,
    fetchDocumentSummaries,
    fetchHanaData,
  } = useOpenOrderDocSum();

  useEffect(() => {
    fetchDocumentSummaries();
  }, [fetchDocumentSummaries]);

  const handleExport = () => {
    console.log('Exporting to Excel', documentSummaries);
    XLSXExport.exportToExcel(documentSummaries, 'Open_Order_Doc_Sum_Report');
  };
  

  if (loading) {
    return <div className="loading-message">Yükleniyor...</div>;
  }

  if (error) {
    return <div className="error-message">Veri yükleme hatası: {error.message}</div>;
  }

  return (
    <ErrorBoundary>
      <div className="open-order-doc-sum-container">
        <div className="open-order-doc-sum-container__header">
          <h3 className="open-order-doc-sum-container__title">
            Açık Sipariş Özeti-Nakliye Montaj
          </h3>

          <div className="open-order-doc-sum-container__last-updated">
        <div className="open-order-doc-sum-container__last-updated">{lastUpdated ? `Son Güncellenme: ${lastUpdated}` : ''}</div>
        </div>
      
          <div className="open-order-doc-sum-container__button-wrapper">
            <button onClick={fetchDocumentSummaries} className="open-order-doc-sum-container__button">
              Yerel Veri Çek
            </button>
            <button onClick={fetchHanaData} className="open-order-doc-sum-container__button">
              HANA Anlık Veri Çek
            </button>
            <button onClick={handleExport} className="open-order-doc-sum-container__button">
              Excel'e Aktar
            </button>
          </div>
        </div>
        <OpenOrderDocSumTable data={documentSummaries} />
      </div>
    </ErrorBoundary>
  );
};

export default OpenOrderDocSumContainer;
