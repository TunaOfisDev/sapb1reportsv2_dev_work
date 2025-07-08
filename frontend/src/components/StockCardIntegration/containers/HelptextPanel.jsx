// path: frontend/src/components/StockCardIntegration/containers/HelptextPanel.jsx

import useHelpTexts from '../hooks/useHelpTexts';
import styles from '../css/HelptextPanel.module.css';

const HelptextPanel = () => {
  const { helpTexts, loading, error } = useHelpTexts();

  if (loading) return <p>Yükleniyor...</p>;
  if (error) return <p className={styles.error}>{error}</p>;
  if (!helpTexts.length) return <p className={styles.empty}>Açıklama verisi bulunamadı.</p>;

  // 🔧 Burada sıralama işlemi
  const sortedHelpTexts = [...helpTexts].sort((a, b) => a.id - b.id);

  return (
    <div className={styles.panel}>
      <h3>Alan Açıklamaları</h3>
      {sortedHelpTexts.map(({ field_name, label, description }) => (
        <div key={field_name} className={styles.item}>
          <strong>{label}</strong>
          <p>{description}</p>
        </div>
      ))}
    </div>
  );
};

export default HelptextPanel;
