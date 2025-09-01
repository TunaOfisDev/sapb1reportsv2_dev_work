// path: frontend/src/components/NexusCore/containers/ReportPlayground/AvailableColumns.jsx
import React from 'react';
import PropTypes from 'prop-types';
import styles from './ReportPlayground.module.scss';
// ### DÜZELTME: İkonun adı 'GripVertical' yerine 'MoreVertical' olmalı ###
import { MoreVertical } from 'react-feather';

/**
 * Kullanıcının raporda kullanabileceği tüm kolonları listeleyen sol panel.
 */
const AvailableColumns = ({ columns }) => {
  return (
    <div className={`${styles.panel} ${styles.availableColumns}`}>
      <h3 className={styles.panelTitle}>Kullanılabilir Kolonlar</h3>
      <div className={styles.panelContent}>
        {columns.length === 0 ? (
          <div className={styles.placeholder}>
            Kaynak veride kolon bulunamadı.
          </div>
        ) : (
          <ul className={styles.columnList}>
            {columns.map(columnName => (
              <li key={columnName} className={styles.columnItem}>
                {/* ### DÜZELTME: Doğru ikon bileşenini kullanıyoruz ### */}
                <MoreVertical className={styles.dragHandle} size={18} />
                <span className={styles.columnName}>{columnName}</span>
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
};

AvailableColumns.propTypes = {
  columns: PropTypes.arrayOf(PropTypes.string).isRequired,
};

export default AvailableColumns;