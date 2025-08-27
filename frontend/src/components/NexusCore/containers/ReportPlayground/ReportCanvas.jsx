// path: frontend/src/components/NexusCore/containers/ReportPlayground/ReportCanvas.jsx
import React from 'react';
import PropTypes from 'prop-types';
import styles from './ReportPlayground.module.scss';
import { Move } from 'react-feather'; // Sürükle-bırak ikonu

/**
 * Kullanıcının seçtiği kolonları ve verinin bir önizlemesini gösteren
 * ana çalışma tuvali. Sürükle-bırak işlemleri için bir bırakma alanı (drop zone)
 * olarak da görev yapacak.
 */
const ReportCanvas = ({ columns, data, onColumnClick, selectedColumnKey }) => {
  // Veri önizlemesi için sadece ilk 5 satırı alalım.
  const previewRows = data.rows ? data.rows.slice(0, 5) : [];

  // Orijinal kolonların pozisyonlarını hızlıca bulmak için bir harita oluşturalım.
  const colIndexMap = data.columns 
    ? data.columns.reduce((acc, colName, index) => {
        acc[colName] = index;
        return acc;
      }, {})
    : {};

  return (
    <div className={`${styles.panel} ${styles.reportCanvas}`}>
      <h3 className={styles.panelTitle}>Rapor Önizlemesi</h3>
      <div className={styles.panelContent}>
        {columns.length === 0 ? (
          <div className={styles.canvasPlaceholder}>
            Rapor oluşturmak için soldaki listeden kolonları buraya sürükleyin.
          </div>
        ) : (
          <div className={styles.previewTableWrapper}>
            <table className={styles.previewTable}>
              <thead>
                <tr>
                  {columns.map(col => (
                    <th 
                      key={col.key}
                      onClick={() => onColumnClick(col.key)}
                      className={selectedColumnKey === col.key ? styles.active : ''}
                    >
                      {col.label}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {previewRows.map((row, rowIndex) => (
                  <tr key={rowIndex}>
                    {columns.map(col => (
                      <td key={col.key}>
                        {/* colIndexMap kullanarak doğru hücre verisini bul */}
                        {String(row[colIndexMap[col.key]] ?? '')}
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
};

ReportCanvas.propTypes = {
  columns: PropTypes.array.isRequired,
  data: PropTypes.shape({
    columns: PropTypes.array,
    rows: PropTypes.array,
  }),
  onColumnClick: PropTypes.func.isRequired,
  selectedColumnKey: PropTypes.string,
};

export default ReportCanvas;