// frontend/src/components/SalesOrderDetail/Container/SalesOrderDetailContainer.js
import React from 'react';
import { Button, Modal } from 'react-bootstrap';
import useSalesOrderDetail from '../hooks/useSalesOrderDetail';
import SalesOrderDetailTable from './SalesOrderDetailTable';
import ErrorMessage from '../utils/ErrorMessage';
import '../css/SalesOrderDetailContainer.css';

const SalesOrderDetailContainer = () => {
  const {
    salesOrderMasters,
    hanaSalesOrderData,
    salesOrderDetail,
    modalVisible,
    loading,
    error,
    fetchSalesOrderMasters,
    fetchHanaSalesOrderData,
    showSalesOrderDetailModal,
    hideModal,
  } = useSalesOrderDetail();

  if (error) {
    return <ErrorMessage message="Satış siparişi detay verileri yüklenirken bir hata oluştu." />;
  }

  return (
    <div className="sales-order-detail-container">
      <div className="sales-order-detail-container__header">
        <h1>Satış Siparişi Detayları</h1>
        <div className="sales-order-detail-container__button-wrapper">
          <Button onClick={fetchSalesOrderMasters} className="sales-order-detail-container__button">
            Yerel Veri Çek
          </Button>
          <Button onClick={fetchHanaSalesOrderData} className="sales-order-detail-container__button">
            HANA Anlık Veri Çek
          </Button>
        </div>
      </div>
      {loading ? (
        <p>Yükleniyor...</p>
      ) : (
        <SalesOrderDetailTable
          salesOrderMasters={salesOrderMasters.length > 0 ? salesOrderMasters : hanaSalesOrderData}
          onRowClick={showSalesOrderDetailModal}
        />
      )}
      <Modal show={modalVisible} onHide={hideModal} size="lg">
        <Modal.Header closeButton>
          <Modal.Title>Sipariş Detayı</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          {salesOrderDetail ? (
            <pre>{JSON.stringify(salesOrderDetail, null, 2)}</pre>
          ) : (
            <p>Detay veri yüklenemedi.</p>
          )}
        </Modal.Body>
      </Modal>
    </div>
  );
};

export default SalesOrderDetailContainer;
