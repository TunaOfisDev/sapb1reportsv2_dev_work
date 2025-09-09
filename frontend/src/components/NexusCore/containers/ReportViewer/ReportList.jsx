// path: frontend/src/components/NexusCore/containers/ReportViewer/ReportList.jsx
import React from 'react';
import PropTypes from 'prop-types';
// ### YENİ: Veri Modelini göstermek için GitMerge ikonunu ekliyoruz
import { PlayCircle, Edit, Trash2, GitMerge } from 'react-feather';
import styles from './ReportList.module.scss';

// Ortak bileşenlerimizi ve yardımcılarımızı import ediyoruz
import Card from '../../components/common/Card/Card';
import Button from '../../components/common/Button/Button';
// ### GÜNCELLEME: formatDateTime yerine formatRelativeTime kullanalım, daha modern.
import { formatRelativeTime } from '../../utils/formatters';

const ReportList = ({ reports = [], onExecute, onEdit, onDelete }) => {
  if (reports.length === 0) {
    return (
      <p className={styles.emptyMessage}>
        {/* ### GÜNCELLEME: Mesaj yeni akışa göre güncellendi ### */}
        Henüz kaydedilmiş bir rapor bulunmuyor. <br />
        Başlamak için "Yeni Rapor Oluştur" butonuna tıklayarak bir Veri Modelinden rapor üretebilirsiniz.
      </p>
    );
  }

  return (
    <div className={styles.reportGrid}>
      {reports.map((report) => (
        <Card
          key={report.id}
          title={report.title}
          className={styles.reportCard}
          headerActions={
            <div className={styles.actions}>
              <Button 
                variant="default" // "secondary" yerine daha yumuşak bir "default" kullanalım
                size="small"
                onClick={() => onEdit(report)} 
                icon={<Edit size={16} />} 
                tooltip="Playground'da Düzenle" 
              />
              <Button 
                variant="danger" 
                size="small"
                onClick={() => onDelete(report.id)} // Sadece ID gönder, hook zaten ID bekler
                icon={<Trash2 size={16} />} 
                tooltip="Sil" 
              />
            </div>
          }
        >
          <div className={styles.cardBody}>
            <p className={styles.description}>{report.description || 'Bu rapor için bir açıklama girilmemiş.'}</p>
            
            {/* ### YENİ: Raporun hangi veri modeline bağlı olduğunu gösteren meta alanı ### */}
            <div className={styles.cardMeta}>
                <GitMerge size={14} className={styles.metaIcon} />
                <span>
                    Veri Modeli: <strong>{report.source_data_app_display || 'Bağlantı Yok'}</strong>
                </span>
            </div>
          </div>

          <div className={styles.cardFooter}>
            <span className={styles.ownerInfo}>
              Sahip: {report.owner || 'Bilinmiyor'}
            </span>
            <span>
              {/* ### GÜNCELLEME: formatRelativeTime kullanımı ### */}
              Güncelleme: {formatRelativeTime(report.updated_at)}
            </span>
          </div>
          
          <Button 
            variant="primary" 
            onClick={() => onExecute(report)} 
            icon={<PlayCircle />} // Component yerine JSX element olarak geçmek daha standarttır
            style={{ width: '100%', marginTop: '1rem' }}
          >
            Raporu Çalıştır
          </Button>
        </Card>
      ))}
    </div>
  );
};

ReportList.propTypes = {
  reports: PropTypes.array.isRequired,
  onExecute: PropTypes.func.isRequired,
  onEdit: PropTypes.func.isRequired,
  onDelete: PropTypes.func.isRequired,
};

export default ReportList;