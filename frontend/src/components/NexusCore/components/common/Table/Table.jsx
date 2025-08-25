// path: frontend/src/components/NexusCore/components/common/Table/Table.jsx
import React from 'react';
import PropTypes from 'prop-types';
import styles from './Table.module.scss';
import Spinner from '../Spinner/Spinner';

/**
 * SQL sorgu sonuçlarını göstermek için tasarlanmış dinamik ve yeniden kullanılabilir Table bileşeni.
 * Yükleniyor, hata ve boş veri durumlarını kendi içinde yönetir.
 */
const Table = ({ data, loading = false, error = null }) => {
  if (loading) {
    return <Spinner />;
  }

  if (error) {
    // API'den gelen daha detaylı hata mesajını göstermek için
    const errorMessage = typeof error === 'string' ? error : (error.message || 'Veri yüklenirken bir hata oluştu.');
    return <div className={styles.messageContainer}>{errorMessage}</div>;
  }

  if (!data || !data.columns || data.columns.length === 0 || !data.rows || data.rows.length === 0) {
    return <div className={styles.messageContainer}>Görüntülenecek veri bulunamadı. Lütfen bir sorgu çalıştırın.</div>;
  }

  const { columns, rows } = data;

  return (
    <div className={styles.tableWrapper}>
      <table className={styles.table}>
        <thead className={styles.thead}>
          <tr className={styles.tr}>
            {columns.map((col, index) => (
              <th key={`${col}-${index}`} className={styles.th}>
                {col}
              </th>
            ))}
          </tr>
        </thead>
        <tbody className={styles.tbody}>
          {rows.map((row, rowIndex) => (
            <tr key={rowIndex} className={styles.tr}>
              {row.map((cell, cellIndex) => (
                <td key={`${rowIndex}-${cellIndex}`} className={styles.td}>
                  {/* Hücre içeriği null veya undefined ise boş string göster */}
                  {cell === null || cell === undefined ? '' : String(cell)}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

Table.propTypes = {
  /** Görüntülenecek veri. { columns: string[], rows: any[][] } formatında olmalı. */
  data: PropTypes.shape({
    columns: PropTypes.arrayOf(PropTypes.string),
    rows: PropTypes.arrayOf(PropTypes.array),
  }),
  /** Veri yüklenirken spinner göstermek için kullanılır. */
  loading: PropTypes.bool,
  /** Bir hata oluştuğunda hata mesajı göstermek için kullanılır. */
  error: PropTypes.oneOfType([PropTypes.object, PropTypes.string]),
};

export default Table;