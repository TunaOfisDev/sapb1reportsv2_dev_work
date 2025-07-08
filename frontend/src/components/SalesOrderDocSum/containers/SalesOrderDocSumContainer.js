// SalesOrderDocSumContainer.js
import React, { useEffect, useCallback, useState } from 'react';
import useSalesOrderDocSum from '../hooks/useSalesOrderDocSum';
import SalesOrderDocSumTable from './SalesOrderDocSumTable';
import XLSXExport from '../utils/XLSXExport';
import { ToastContainer, toast } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import '../css/SalesOrderDocSumContainer.css';

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

const SalesOrderDocSumContainer = () => {
  const {
    lastUpdated,
    loading,
    error,
    documentSummaries,
    fetchDocumentSummaries,
    fetchHanaDataAndRefresh,
  } = useSalesOrderDocSum();

  const [tableRef, setTableRef] = useState(null);

  useEffect(() => {
    const initialLoad = async () => {
      try {
        await fetchDocumentSummaries();
      } catch (err) {
        console.error('İlk yüklemede bir hata oluştu:', err);
        toast.error('Veri yüklenirken bir hata oluştu');
      }
    };
    initialLoad();
  }, [fetchDocumentSummaries]);

  const handleFetchLocalData = async () => {
    try {
      await fetchDocumentSummaries();
      toast.success('Yerel veriler başarıyla güncellendi');
    } catch (err) {
      console.error('Yerel veri çekilirken bir hata oluştu:', err);
      toast.error('Yerel veri çekilirken bir hata oluştu');
    }
  };

  const handleFetchHanaData = async () => {
    try {
      await fetchHanaDataAndRefresh();
      toast.success('HANA verileri başarıyla güncellendi');
    } catch (err) {
      console.error('HANA veri çekilirken bir hata oluştu:', err);
      toast.error('HANA verisi çekilirken bir hata oluştu');
    }
  };

  const handleExport = useCallback(() => {
    if (!tableRef?.getFilteredRows) {
      toast.error('Tablo referansı bulunamadı');
      return;
    }

    try {
      const filteredRows = tableRef.getFilteredRows();
      const totals = tableRef.getTotals();

      if (filteredRows?.length) {
        XLSXExport.exportToExcel(
          filteredRows,
          'Acik_Siparis_Ozeti',
          totals
        );
        toast.success('Excel dosyası başarıyla oluşturuldu');
      } else {
        toast.warning('Dışa aktarılacak veri bulunamadı');
      }
    } catch (error) {
      console.error('Excel export hatası:', error);
      toast.error('Excel dosyası oluşturulurken bir hata oluştu');
    }
  }, [tableRef]);

  if (loading) {
    return <div className="loading-message">Yükleniyor...</div>;
  }

  if (error) {
    return <div className="error-message">Veri yükleme hatası: {error.message}</div>;
  }

  return (
    <ErrorBoundary>
      <div className="sales-order-doc-sum-container">
        <ToastContainer 
          position="top-right"
          autoClose={3000}
          hideProgressBar={false}
          newestOnTop={false}
          closeOnClick
          rtl={false}
          pauseOnFocusLoss
          draggable
          pauseOnHover
        />
        <div className="sales-order-doc-sum-container__header">
          <h3 className="sales-order-doc-sum-container__title">
            Satis Siparis Belge Kontrol
          </h3>
          <div className="sales-order-doc-sum-container__last-updated">
            {lastUpdated ? `Son Güncellenme: ${lastUpdated}` : ''}
          </div>
          <div className="sales-order-doc-sum-container__button-wrapper">
            <button 
              onClick={handleFetchLocalData} 
              className="sales-order-doc-sum-container__button"
              disabled={loading}
            >
              Yerel Veri Çek
            </button>
            <button 
              onClick={handleFetchHanaData} 
              className="sales-order-doc-sum-container__button"
              disabled={loading}
            >
              HANA Anlık Veri Çek
            </button>
            <button 
              onClick={handleExport} 
              className="sales-order-doc-sum-container__button"
              disabled={loading || !documentSummaries?.length}
            >
              Excel e Aktar
            </button>
          </div>
        </div>
        {documentSummaries ? (
          <SalesOrderDocSumTable 
            documentSummaries={documentSummaries}
            ref={setTableRef}
          />
        ) : null}
      </div>
    </ErrorBoundary>
  );
};

export default SalesOrderDocSumContainer;