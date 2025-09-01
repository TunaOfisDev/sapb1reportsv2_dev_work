// path: frontend/src/components/NexusCore/containers/ReportPlayground/PropertiesPanel.jsx
import React from 'react';
import PropTypes from 'prop-types';
import styles from './ReportPlayground.module.scss'; // Ortak stil dosyasını kullanıyoruz

import Input from '../../components/common/Input/Input';

/**
 * ReportPlayground'da seçilen bir kolonun özelliklerini düzenlemek için
 * kullanılan sağ panel bileşeni.
 */
const PropertiesPanel = ({ selectedColumn, onUpdateColumn }) => {
  // Eğer hiçbir kolon seçilmemişse, bir yardımcı metin göster.
  if (!selectedColumn) {
    return (
      <div className={`${styles.panel} ${styles.propertiesPanel}`}>
        <div className={styles.placeholder}>
          Özelliklerini düzenlemek için bir kolon seçin.
        </div>
      </div>
    );
  }

  // Kolon özelliklerini (label, visible) değiştiren handler fonksiyonları
  const handleLabelChange = (e) => {
    onUpdateColumn(selectedColumn.key, { label: e.target.value });
  };

  const handleVisibilityChange = (e) => {
    onUpdateColumn(selectedColumn.key, { visible: e.target.checked });
  };

  return (
    <div className={`${styles.panel} ${styles.propertiesPanel}`}>
      <h3 className={styles.panelTitle}>Kolon Özellikleri</h3>
      <div className={styles.panelContent}>
        <div className={styles.propertyGroup}>
          <span className={styles.originalName}>
            Orijinal Ad: <strong>{selectedColumn.key}</strong>
          </span>
        </div>

        <div className={styles.propertyGroup}>
          <Input
            id={`prop-label-${selectedColumn.key}`}
            label="Kolon Başlığı"
            value={selectedColumn.label}
            onChange={handleLabelChange}
            helperText="Raporda görünecek olan başlık."
          />
        </div>

        <div className={styles.propertyGroup}>
            <label htmlFor={`prop-visible-${selectedColumn.key}`} className={styles.checkboxLabel}>
                <input
                    type="checkbox"
                    id={`prop-visible-${selectedColumn.key}`}
                    checked={selectedColumn.visible}
                    onChange={handleVisibilityChange}
                />
                Kolonu Göster
            </label>
        </div>
      </div>
    </div>
  );
};

PropertiesPanel.propTypes = {
  selectedColumn: PropTypes.shape({
    key: PropTypes.string.isRequired,
    label: PropTypes.string.isRequired,
    visible: PropTypes.bool.isRequired,
  }),
  onUpdateColumn: PropTypes.func.isRequired,
};

export default PropertiesPanel;