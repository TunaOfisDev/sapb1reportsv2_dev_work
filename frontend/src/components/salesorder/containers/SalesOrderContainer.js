// frontend/src/components/salesorder/containers/SalesOrderContainer.js
import React, { useEffect } from 'react';
import { Button } from 'react-bootstrap';
import UseSalesOrder from '../hooks/UseSalesOrder';
import SalesOrderTable from './SalesOrderTable';
import ErrorMessage from '../utils/ErrorMessage'; 
import '../css/SalesOrderContainer.css'; 

const SalesOrderContainer = () => {
  const {
    localSalesOrder,
    instantSalesOrder,
    loading,
    error,
    fetchLocalSalesOrder,
    fetchInstantSalesOrder,
  } = UseSalesOrder();

  useEffect(() => {
    fetchLocalSalesOrder();
  }, [fetchLocalSalesOrder]);

  if (error) {
    return <ErrorMessage message="Veri yüklenirken bir hata oluştu." />;
  }

  return (
    <div className="sales-order-container">
      <div className="sales-order-container__header">
        <h1>Satış Siparişleri</h1>
        <div className="sales-order-container__button-wrapper">
          <Button onClick={fetchLocalSalesOrder} className="sales-order-container__button">
            Yerel Veri Çek
          </Button>
          <Button onClick={fetchInstantSalesOrder} className="sales-order-container__button">
            HANA Anlık Veri Çek
          </Button>
        </div>
      </div>
      {loading ? (
        <p>Yükleniyor...</p>
      ) : (
        <SalesOrderTable salesOrders={localSalesOrder.length > 0 ? localSalesOrder : instantSalesOrder} />
      )}
    </div>
  );
};

export default SalesOrderContainer;


