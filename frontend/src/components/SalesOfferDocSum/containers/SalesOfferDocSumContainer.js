// frontend/src/components/SalesOfferDocSum/containers/SalesOfferDocSumContainer.js
import React, { useEffect, useMemo, useCallback } from 'react';
import useSalesOfferDocSum from '../hooks/useSalesOfferDocSum';
import SalesOfferDocSumTable from './SalesOfferDocSumTable';
import XLSXExport from '../utils/XLSXExport'; 
import formatDate from '../utils/DateFormat';
import '../css/SalesOfferDocSumContainer.css';

class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null, errorInfo: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true };
  }

  componentDidCatch(error, errorInfo) {
    this.setState({
      error: error,
      errorInfo: errorInfo
    });
    console.error('Hata yakalandı:', error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="error-boundary">
          <h1>Bir şeyler yanlış gitti.</h1>
          <details style={{ whiteSpace: 'pre-wrap' }}>
            {this.state.error && this.state.error.toString()}
            <br />
            {this.state.errorInfo && this.state.errorInfo.componentStack}
          </details>
        </div>
      );
    }

    return this.props.children; 
  }
}

const SalesOfferDocSumContainer = () => {
  const {
    lastUpdated,
    loading: docSumLoading,
    error: docSumError,
    documentSummaries,
    fetchDocumentSummaries,
    fetchHanaData,
  } = useSalesOfferDocSum();

  useEffect(() => {
    fetchDocumentSummaries();
  }, [fetchDocumentSummaries]);

  const handleExport = useCallback(() => {
    console.log('Excel\'e aktarılıyor', documentSummaries);
    XLSXExport.exportToExcel(documentSummaries, 'sales_Offer_Doc_Sum_Report');
  }, [documentSummaries]);

  const renderContent = useMemo(() => {
    if (docSumLoading) {
      return <div className="loading-message">Yükleniyor...</div>;
    }
    if (docSumError) {
      return <div className="error-message">Veri yükleme hatası: {docSumError?.message || docSumError}</div>;
    }

    return <SalesOfferDocSumTable data={documentSummaries} />;
  }, [docSumLoading, docSumError, documentSummaries]);

  return (
    <ErrorBoundary>
      <div className="sales-offer-doc-sum-container">
        <div className="sales-offer-doc-sum-container__header">
          <div className="sales-offer-doc-sum-container__header-group sales-offer-doc-sum-container__header-group--left">
            <h3 className="sales-offer-doc-sum-container__title">
              Satış Teklifleri Belge Kontrol
            </h3>
          </div>
          <div className="sales-offer-doc-sum-container__header-group sales-offer-doc-sum-container__header-group--center">
            <div className="sales-offer-doc-sum-container__last-updated">
              {lastUpdated ? `Son Güncellenme: ${formatDate(lastUpdated)}` : ''}
            </div>
          </div>
          <div className="sales-offer-doc-sum-container__header-group sales-offer-doc-sum-container__header-group--right">
            <div className="sales-offer-doc-sum-container__actions">
              <button onClick={fetchHanaData} className="sales-offer-doc-sum-container__button">
                HANA Anlık Veri Çek
              </button>
              <button onClick={handleExport} className="sales-offer-doc-sum-container__button">
                Excel e Aktar
              </button>
            </div>
          </div>
        </div>

        <div className="sales-offer-doc-sum-container__content">
          {renderContent}
        </div>
      </div>
    </ErrorBoundary>
  );
};

export default SalesOfferDocSumContainer;