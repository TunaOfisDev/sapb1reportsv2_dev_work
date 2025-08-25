// path: frontend/src/components/NexusCore/containers/ConnectionManager/ConnectionList.jsx
import React from 'react';
import PropTypes from 'prop-types';
import { Edit, Trash2, PlayCircle, Database } from 'react-feather';
import Button from '../../components/common/Button/Button';
// Bu bileşen, ana kapsayıcısı ile aynı stil dosyasını paylaşabilir.
import styles from './ConnectionManager.module.scss'; 

/**
 * Mevcut veritabanı bağlantılarını bir liste halinde gösteren sunumsal bileşen.
 * Tüm aksiyonlar (düzenleme, silme, test etme) parent bileşenden gelen
 * fonksiyonlar aracılığıyla yönetilir.
 */
const ConnectionList = ({ connections, onEdit, onDelete, onTest }) => {
  // Eğer hiç bağlantı yoksa, kullanıcıya bilgilendirici bir mesaj gösterilir.
  if (!connections || connections.length === 0) {
    return (
      <div className={styles.emptyState}>
        <Database size={48} />
        <p>Henüz bir veri kaynağı eklenmemiş.</p>
        <span>"Yeni Bağlantı Ekle" butonu ile başlayabilirsiniz.</span>
      </div>
    );
  }

  return (
    <ul className={styles.connectionList}>
      {connections.map((conn) => (
        <li key={conn.id} className={styles.connectionItem}>
          <div className={styles.connectionInfo}>
            <span className={styles.connectionTitle}>{conn.title}</span>
            <span className={styles.connectionType}>{conn.db_type}</span>
          </div>
          <div className={styles.connectionActions}>
            <Button variant="secondary" onClick={() => onTest(conn.id)} IconComponent={PlayCircle} title="Bağlantıyı Test Et">
              Test Et
            </Button>
            <Button variant="secondary" onClick={() => onEdit(conn)} IconComponent={Edit} title="Düzenle">
              Düzenle
            </Button>
            <Button variant="danger" onClick={() => onDelete(conn.id)} IconComponent={Trash2} title="Sil">
              Sil
            </Button>
          </div>
        </li>
      ))}
    </ul>
  );
};

// Bileşenin hangi propları ne türde beklediğini tanımlamak, kod kalitesi için kritiktir.
ConnectionList.propTypes = {
  /** Görüntülenecek bağlantıların listesi */
  connections: PropTypes.arrayOf(PropTypes.shape({
    id: PropTypes.number.isRequired,
    title: PropTypes.string.isRequired,
    db_type: PropTypes.string,
  })).isRequired,
  /** Düzenle butonuna tıklandığında tetiklenecek fonksiyon */
  onEdit: PropTypes.func.isRequired,
  /** Sil butonuna tıklandığında tetiklenecek fonksiyon */
  onDelete: PropTypes.func.isRequired,
  /** Test Et butonuna tıklandığında tetiklenecek fonksiyon */
  onTest: PropTypes.func.isRequired,
};

export default ConnectionList;