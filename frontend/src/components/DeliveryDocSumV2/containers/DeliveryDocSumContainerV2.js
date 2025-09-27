// frontend/src/components/DeliveryDocSumV2/containers/DeliveryDocSumContainerV2.js
import React from 'react';
import useDeliveryDocSum from '../hooks/useDeliveryDocSum';
import DeliveryDocSumTable from './DeliveryDocSumTable';
import useAuth from '../../../auth/useAuth';
import LastUpdateDateTime from '../utils/LastUpdateDateTime';
import '../css/DeliveryDocSumContainer.css';

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

const DeliveryDocSumContainerV2 = () => {
  const { isAuthenticated } = useAuth();
  
  const {
    data,
    isLoading,
    fetchHana,
    loadLocalData, // Hook'tan loadLocalData fonksiyonunu çekiyoruz
    columnNames // Hook'tan columnNames'i çekiyoruz
  } = useDeliveryDocSum();

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
      <div className="delivery-doc-sum-container">
        <div className="delivery-doc-sum-container__header">
          <h1 className="delivery-doc-sum-container__title">
            Sevkiyat Takip
          </h1>
          <div>
            Son güncelleme tarihi: <LastUpdateDateTime datetime={data.updated_at} />
          </div>
          <div className="delivery-doc-sum-container__button-wrapper">
            <button onClick={handleFetchLocalData} className="delivery-doc-sum-container__button">
              Yerel Veri Çek
            </button>
            <button onClick={handleFetchHanaData} className="delivery-doc-sum-container__button">
              HANA Veri Çek
            </button>
          </div>
        </div>
        <DeliveryDocSumTable data={data} columnNames={columnNames} /> {/* columnNames prop olarak geçiriliyor */}
      </div>
    </ErrorBoundary>
  );
};

export default DeliveryDocSumContainerV2;
