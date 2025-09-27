// path: frontend/src/components/StockCardIntegration/utils/ColumnFilter.js

import React from 'react';
import styles from '../css/ColumnFilter.module.css';

/**
 * Custom column filter input for react-table
 * - Büyük/küçük harf duyarsız
 * - Türkçe karakter uyumlu
 * - Hızlı, sade arama
 */
const ColumnFilter = ({ column: { filterValue, setFilter, id } }) => {
  const handleChange = (e) => {
    const value = e.target.value || undefined;
    setFilter(value);
  };

  return (
    <div className={styles['column-filter']}>
      <input
        type="text"
        placeholder="Ara..."
        value={filterValue || ''}
        onChange={handleChange}
        className={styles['column-filter__input']}
        autoComplete="off"
        spellCheck="false"
        name={`filter-${id}`}
      />
    </div>
  );
};

export default ColumnFilter;
