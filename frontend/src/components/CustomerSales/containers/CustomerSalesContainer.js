// frontend/src/components/customersales/containers/CustomerSalesContainer.js
import React from 'react';
import { Button } from 'react-bootstrap';
import useCustomerSales from '../hooks/useCustomerSales';
import CustomerSalesTable from './CustomerSalesTable';
import ErrorMessage from '../utils/ErrorMessage';
import '../css/CustomerSalesContainer.css';

const CustomerSalesContainer = () => {
  const {
    customerSalesOrders,
    hanaCustomerSalesData,
    lastUpdated,
    loading,
    error,
    fetchCustomerSalesOrders,
    fetchHanaCustomerSalesData,
    fetchLastUpdatedTime,
    exportCustomerSalesToXLSX // Yeni eklenen export fonksiyonu
  } = useCustomerSales();

  // HANA verisini çekerken aynı zamanda son güncellenme zamanını da güncelleyen fonksiyon
  const fetchHanaDataAndUpdateTime = async () => {
    await fetchHanaCustomerSalesData(); // HANA verisini çek
    fetchLastUpdatedTime(); // Son güncellenme zamanını güncelle
  };

  if (error) {
    return <ErrorMessage message="Müşteri satış sipariş verileri yüklenirken bir hata oluştu." />;
  }

  return (
    <div className="customer-sales-container">
      <div className="customer-sales-container__header">
        <h1 className="customer-sales-container__title">Müşteri Satış Siparişleri Aylık</h1>
        {lastUpdated && (
          <p className="customer-sales-container__last-updated">Son Güncellenme: {lastUpdated}</p>
        )}
        <div className="customer-sales-container__button-wrapper">
          <Button onClick={fetchCustomerSalesOrders} className="customer-sales-container__button">
            Yerel Veri Çek
          </Button>
          <Button onClick={fetchHanaDataAndUpdateTime} className="customer-sales-container__button">
            HANA Anlık Veri Çek
          </Button>
          <Button onClick={exportCustomerSalesToXLSX} className="customer-sales-container__button">
            Excel'e Aktar
          </Button>
        </div>
      </div>
      {loading ? (
        <p>Yükleniyor...</p>
      ) : customerSalesOrders.length > 0 || hanaCustomerSalesData.length > 0 ? (
        <CustomerSalesTable
          customerSales={customerSalesOrders.length > 0 ? customerSalesOrders : hanaCustomerSalesData}
          loading={loading}
          error={error}
        />
      ) : (
        <p>Veri bulunamadı. Lütfen veri çekmek için ilgili butona basınız.</p>
      )}
    </div>
  );
};

export default CustomerSalesContainer;
