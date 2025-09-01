// path: frontend/src/components/NexusCore/containers/ReportViewer/ReportList.jsx
import React from 'react';
import PropTypes from 'prop-types';
import { PlayCircle, Edit, Trash2 } from 'react-feather';
import styles from './ReportList.module.scss';

// Ortak bileşenlerimizi ve yardımcılarımızı import ediyoruz
import Card from '../../components/common/Card/Card';
import Button from '../../components/common/Button/Button';
import { formatDateTime } from '../../utils/formatters';

const ReportList = ({ reports = [], onExecute, onEdit, onDelete }) => {
  if (reports.length === 0) {
    return (
      <p className={styles.emptyMessage}>
        Henüz kaydedilmiş bir rapor bulunmuyor. <br />
        'Çalışma Alanı'na giderek yeni bir sorgu çalıştırıp, sonuçlar üzerinden bir rapor oluşturabilirsiniz.
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
              <Button variant="secondary" onClick={() => onEdit(report)} IconComponent={Edit} title="Playground'da Düzenle" />
              <Button variant="danger" onClick={() => onDelete(report)} IconComponent={Trash2} title="Sil" />
            </div>
          }
        >
          <div className={styles.cardBody}>
            <p>{report.description || 'Bu rapor için bir açıklama girilmemiş.'}</p>
          </div>
          <div className={styles.cardFooter}>
            <span className={styles.ownerInfo}>
              Oluşturan: {report.owner || 'Bilinmiyor'}
            </span>
            <span>
              Son Güncelleme: {formatDateTime(report.updated_at)}
            </span>
          </div>
          <Button 
            variant="primary" 
            onClick={() => onExecute(report)} 
            IconComponent={PlayCircle}
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