// path: frontend/src/components/StockCardIntegration/views/PreviewTable.jsx
import PropTypes from 'prop-types';
import styles from '../css/PreviewTable.module.css';   // dikkat: ../css

const PreviewTable = ({ data }) => {
  if (!data.length) return null;
  const columns = Object.keys(data[0]);

  return (
    <div className={styles['preview-wrapper']}>
      <table className={styles['preview-table']}>
        <thead>
          <tr>
            {columns.map((col) => (
              <th key={col}>{col}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {data.slice(0, 100).map((row, idx) => (
            <tr key={idx}>
              {columns.map((col) => (
                <td key={col}>{row[col]}</td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
      {data.length > 100 && (
        <p className={styles['preview-note']}>
          İlk 100 kayıt gösteriliyor. Toplam: <strong>{data.length}</strong>
        </p>
      )}
    </div>
  );
};

PreviewTable.propTypes = {
  data: PropTypes.arrayOf(PropTypes.object).isRequired,
};

export default PreviewTable;
