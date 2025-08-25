/* path: frontend/src/components/NexusCore/containers/VirtualTableWorkspace/DataTable.js */

import React from 'react';
import styles from './DataTable.module.scss';
/* Bu bileşenlerin `components/common/` altında daha önce oluşturulduğunu varsayıyoruz. */
/* import { Spinner } from '../../components/common/Spinner/Spinner'; */

/**
 * API'den gelen sorgu sonucunu dinamik olarak bir tabloda gösterir.
 * @param {object} props
 * @param {boolean} props.loading - Verinin yüklenip yüklenmediği durumu.
 * @param {Error | null} props.error - Veri çekme sırasında oluşan hata.
 * @param {{columns: string[], rows: object[]}} props.data - Tabloda gösterilecek veri.
 * @param {object} props.columnMetadata - Kolonların görünürlük ve etiket bilgilerini tutan nesne.
 */
const DataTable = ({ loading, error, data, columnMetadata }) => {
  // 1. Duruma göre arayüzü çiz: Yükleniyor, Hata, Boş Veri, Başarılı Veri
  if (loading) {
    return (
      <div className={styles.messageContainer}>
        {/* <Spinner />  // Gerçek Spinner bileşeni buraya gelecek */}
        <span>Veriler Yükleniyor...</span>
      </div>
    );
  }

  if (error) {
    return (
      <div className={styles.messageContainer}>
        <div className={styles.errorMessage}>
          <strong>Hata:</strong> {error.message || 'Veriler alınamadı.'}
        </div>
      </div>
    );
  }

  if (!data || !data.rows || data.rows.length === 0) {
    return (
      <div className={styles.messageContainer}>
        <span>Görüntülenecek veri yok. Lütfen bir sorgu çalıştırın.</span>
      </div>
    );
  }

  // 2. columnMetadata'ya göre gösterilecek kolonları belirle.
  const visibleColumns = data.columns.filter(
    (colName) => columnMetadata?.[colName]?.visible !== false
  );

  if (visibleColumns.length === 0) {
    return (
      <div className={styles.messageContainer}>
        <span>Tüm kolonlar gizlenmiş. Lütfen kolon ayarlarından en az birini görünür yapın.</span>
      </div>
    );
  }

  // 3. Veri varsa tabloyu çiz.
  return (
    <div className={styles.dataTableWrapper}>
      <table className={styles.dataTable}>
        <thead className={styles.dataTable__header}>
          <tr>
            {visibleColumns.map((colName) => (
              <th key={colName} className={styles.dataTable__headerCell}>
                {columnMetadata?.[colName]?.label || colName}
              </th>
            ))}
          </tr>
        </thead>
        <tbody className={styles.dataTable__body}>
          {data.rows.map((row, rowIndex) => (
            <tr key={rowIndex} className={styles.dataTable__row}>
              {visibleColumns.map((colName) => (
                <td key={`${rowIndex}-${colName}`} className={styles.dataTable__cell}>
                  {String(row[colName])}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default DataTable;