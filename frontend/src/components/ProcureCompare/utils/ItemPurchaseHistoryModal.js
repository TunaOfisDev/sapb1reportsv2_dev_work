// File: frontend/src/components/ProcureCompare/utils/ItemPurchaseHistoryModal.js

import React, { useEffect } from 'react';
import { Modal, Table, Spin } from 'antd';
import { useItemPurchaseHistory } from '../hooks/useItemPurchaseHistory';
import formatNumber from '../utils/FormatNumber';
import '../css/ItemPurchaseHistoryModal.css';

/**
 * Kalem geçmişi popup'ı
 */
const ItemPurchaseHistoryModal = ({ visible, onClose, itemCode, itemName }) => {
  const { data, loading, loadItemPurchaseHistory, source } = useItemPurchaseHistory();

  useEffect(() => {
    if (visible && itemCode) {
      loadItemPurchaseHistory(itemCode);
    }
  }, [visible, itemCode, loadItemPurchaseHistory]);

  const columns = [
    { title: 'Belge No', dataIndex: 'BelgeNo', key: 'BelgeNo' },
    { title: 'Tarih', dataIndex: 'Tarih', key: 'Tarih' },
    {
      title: 'Tedarikçi',
      dataIndex: 'TedarikciAdi',
      key: 'TedarikciAdi',
      render: (value) => (
        <div className="item-purchase-history-modal__cell--tedarikci" title={value}>
          {value?.length > 8 ? `${value.slice(0, 8)}…` : value}
        </div>
      )
    },
    {
      title: 'Miktar',
      dataIndex: 'Miktar',
      key: 'Miktar',
      render: value => (
        <div className="item-purchase-history-modal__cell--number">{formatNumber(value)}</div>
      )
    },
    {
      title: 'Net Fiyat (Döviz)',
      dataIndex: 'NetFiyat_Doviz',
      key: 'NetFiyat_Doviz',
      render: value => (
        <div className="item-purchase-history-modal__cell--number">{formatNumber(value, 3)}</div>
      )
    },
    { title: 'Döviz', dataIndex: 'Doviz', key: 'Doviz' },
    {
      title: 'Kur',
      dataIndex: 'Kur',
      key: 'Kur',
      render: value => (
        <div className="item-purchase-history-modal__cell--number">{formatNumber(value, 3)}</div>
      )
    },
    {
      title: 'Toplam Tutar (Döviz)',
      dataIndex: 'ToplamTutar_Doviz',
      key: 'ToplamTutar_Doviz',
      render: value => (
        <div className="item-purchase-history-modal__cell--number">{formatNumber(value)}</div>
      )
    },
    {
      title: 'Net Fiyat (YPB)',
      dataIndex: 'NetFiyat_YPB',
      key: 'NetFiyat_YPB',
      render: value => (
        <div className="item-purchase-history-modal__cell--number">{formatNumber(value, 3)}</div>
      )
    },
    {
      title: 'Toplam Tutar (YPB)',
      dataIndex: 'ToplamTutar_YPB',
      key: 'ToplamTutar_YPB',
      render: value => (
        <div className="item-purchase-history-modal__cell--number">{formatNumber(value)}</div>
      )
    }
  ];

  return (
    <Modal
  open={visible}
  onCancel={onClose}
  footer={null}
  title={`Satınalma Geçmişi: ${itemCode}${itemName ? ' - ' + itemName : ''}`}
  className="item-purchase-history-modal"
  width={720}                
  centered
  destroyOnClose={true}
>
  <div className="item-purchase-history-modal__content-wrapper">
    {loading ? (
      <div className="item-purchase-history-modal__loading">
        <Spin size="large" />
      </div>
    ) : (
      <Table
        className="item-purchase-history-modal__table"
        columns={columns}
        dataSource={data || []}
        pagination={{ pageSize: 10 }}
        scroll={{ x: '100%' }}  
        size="small"            
        rowKey="BelgeNo"
        bordered               
      />
    )}

        <div className="item-purchase-history-modal__source-indicator">
          {source === 'cache' ? (
            <span className="item-purchase-history-modal__indicator-green">🟢 RedisCache</span>
          ) : (
            <span className="item-purchase-history-modal__indicator-red">🔴 HANA Online</span>
          )}
        </div>
      </div>
    </Modal>
  );
};

export default ItemPurchaseHistoryModal;