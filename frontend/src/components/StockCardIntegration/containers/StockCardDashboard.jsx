// path: frontend/src/components/StockCardIntegration/containers/StockCardDashboard.jsx

import { useState } from 'react';
import styles from '../css/StockCardDashboard.module.css';
import {
  StockCardForm,
  BulkCreateForm,
  UpdateForm,
  StockCardList
} from '../index';
import HelptextPanel from './HelptextPanel';
import ProductPriceListDashboard from './ProductPriceListDashboard'; // ✅ yeni bileşen eklendi

const StockCardDashboard = () => {
  const [activeTab, setActiveTab] = useState('form');

  const renderActiveTab = () => {
    switch (activeTab) {
      case 'form':
        return (
          <div className={styles['stock-dashboard__split']}>
            <div className={styles['stock-dashboard__left']}>
              <StockCardForm />
            </div>
            <div className={styles['stock-dashboard__right']}>
              <HelptextPanel />
            </div>
          </div>
        );
      case 'bulk':
        return <BulkCreateForm />;
      case 'update':
        return <UpdateForm />;
      case 'list':
        return <StockCardList />;
      case 'price':
        return <ProductPriceListDashboard />; // ✅ yeni sekme içeriği
      default:
        return null;
    }
  };

  return (
    <div className={styles['stock-dashboard']}>
      <div className={styles['stock-dashboard__header']}>
        <h1 className={styles['stock-dashboard__title']}>Stok Kartı Merkezi</h1>
      </div>

      <div className={styles['stock-dashboard__tabs']}>
        {[
          { key: 'form', label: '➕ Stok Kartı Ekle' },
          { key: 'bulk', label: '📂 Çoklu Yükleme' },
          { key: 'update', label: '✏️ Güncelleme' },
          { key: 'list', label: '📄 SAP Listesi' },
          { key: 'price', label: '💶 Ürün Fiyat Listesi' }, // ✅ yeni sekme
        ].map((tab) => (
          <div
            key={tab.key}
            className={`${styles['stock-dashboard__tab']} ${
              activeTab === tab.key ? styles['stock-dashboard__tab--active'] : ''
            }`}
            onClick={() => setActiveTab(tab.key)}
          >
            {tab.label}
          </div>
        ))}
      </div>

      <div className={styles['stock-dashboard__content']}>
        {renderActiveTab()}
      </div>
    </div>
  );
};

export default StockCardDashboard;
