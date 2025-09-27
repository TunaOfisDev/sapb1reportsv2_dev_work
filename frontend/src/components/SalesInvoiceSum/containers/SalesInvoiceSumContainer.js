// frontend/src/components/SalesInvoiceSum/containers/SalesInvoiceSumContainer.js
import React from 'react';
import useSalesInvoiceSum from '../hooks/useSalesInvoiceSum';
import SalesInvoiceSumTable from './SalesInvoiceSumTable';
import useAuth from '../../../auth/useAuth';
import LastUpdateDateTime from '../utils/LastUpdateDateTime';
import '../css/SalesInvoiceSumContainer.css';

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

const SalesInvoiceSumContainer = () => {
  const { isAuthenticated } = useAuth();

  const {
    data,
    isLoading,
    fetchHana,
    loadLocalData,
    loadDynamicNameColumns, // <-- hook'tan eklendi
    columnNames,
    lastUpdated,
    isHanaButtonDisabled
  } = useSalesInvoiceSum();

  const handleFetchHanaData = async () => {
    if (isAuthenticated) {
      try {
        await fetchHana();
      } catch (error) {
        console.error('HANA Veri Çekme Hatası:', error);
      }
    } else {
      console.log('Kullanıcı kimlik doğrulaması gerekli.');
    }
  };

  const handleFetchLocalData = async () => {
    if (isAuthenticated) {
      try {
        await loadLocalData();
        await loadDynamicNameColumns(); // <-- dinamik kolon isimlerini de güncelle
      } catch (error) {
        console.error('Yerel Veri Çekme Hatası:', error);
      }
    } else {
      console.log('Kullanıcı kimlik doğrulaması gerekli.');
    }
  };

  if (isLoading) {
    return <div className="loading-message">Yükleniyor...</div>;
  }

  if (!isAuthenticated) {
    return <div>Lütfen erişim için giriş yapın.</div>;
  }

  return (
    <ErrorBoundary>
      <div className="sales-invoice-sum-container">
        <div className="sales-invoice-sum-container__header">
          <h1 className="sales-invoice-sum-container__title">
            Satış Faturası Özeti
          </h1>
          <div>
            Son güncelleme tarihi: <LastUpdateDateTime datetime={lastUpdated} />
          </div>
          <div className="sales-invoice-sum-container__button-wrapper">
            <button
  onClick={handleFetchLocalData}
  className="sales-invoice-sum-container__button"
  disabled={isLoading}          // ← istersen
>
  {isLoading ? 'Yükleniyor…' : 'Yerel Veri Çek'}
</button>
            <button
              onClick={handleFetchHanaData}
              className="sales-invoice-sum-container__button"
              disabled={isHanaButtonDisabled}
            >
              {isHanaButtonDisabled ? 'Veri Çekiliyor...' : 'HANA Veri Çek'}
            </button>
          </div>
        </div>
        <SalesInvoiceSumTable data={data} columnNames={columnNames} />
      </div>
    </ErrorBoundary>
  );
};

export default SalesInvoiceSumContainer;
