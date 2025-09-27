// File: frontend/src/components/ProcureCompare/components/SyncButton.jsx

import React from 'react';
import styles from '../css/ProcureCompare.module.css';

/**
 * HANA'dan veri senkronizasyonu başlatmak için buton.
 * Props:
 * - onClick: tıklama işlevi
 * - loading: true ise spinner gösterilir
 */
const SyncButton = ({ onClick, loading }) => {
  return (
    <button
      className={styles['procure-compare__sync-button']}
      onClick={onClick}
      disabled={loading}
    >
      {loading ? 'Senkr. Yapılıyor...' : 'HANA\'dan Veriyi Çek'}
    </button>
  );
};

export default SyncButton;
