// path: frontend/src/components/StockCardIntegration/containers/StockCardDashboard.jsx

import { useState } from 'react';
import styles from '../css/StockCardDashboard.module.css'; // ✅ module.css olarak import edildi
import { StockCardForm, BulkCreateForm, UpdateForm, StockCardList } from '../index';
import HelptextPanel from '../containers/HelptextPanel';

const StockCardDashboard = () => {
  const [activeTab, setActiveTab] = useState('form');

  const renderActiveTab = () => {
    if (activeTab === 'form') {
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
    }
    if (activeTab === 'bulk') return <BulkCreateForm />;
    if (activeTab === 'update') return <UpdateForm />;
    if (activeTab === 'list') return <StockCardList />;
    return null;
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