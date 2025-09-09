// path: frontend/src/components/NexusCore/containers/ReportViewer/SelectDataAppModal.jsx

import React, { useEffect } from 'react';
import PropTypes from 'prop-types';
import { useNavigate } from 'react-router-dom';
import { useDataApps } from '../../hooks/useDataApps';
import Modal from '../../components/common/Modal/Modal';
import Spinner from '../../components/common/Spinner/Spinner';
import Button from '../../components/common/Button/Button';
import { GitMerge, ChevronRight } from 'react-feather';
import styles from './SelectDataAppModal.module.scss';

/**
 * Kullanıcı "Yeni Rapor" butonuna bastığında hangi Veri Modeli (DataApp) üzerinden
 * ilerleyeceğini seçmesi için gösterilen modal.
 */
const SelectDataAppModal = ({ isOpen, onClose }) => {
  const { dataApps, isLoading, loadDataApps } = useDataApps();
  const navigate = useNavigate();

  // Modal her açıldığında (veya ilk açıldığında) DataApp listesini yükle
  useEffect(() => {
    if (isOpen) {
      loadDataApps();
    }
  }, [isOpen, loadDataApps]);

  /**
   * Kullanıcı bir veri modeli seçtiğinde tetiklenir.
   * Modalı kapatır ve kullanıcıyı Playground'a (o modelin ID'si ile) yönlendirir.
   */
  const handleSelectApp = (app) => {
    onClose(); // Modalı kapat
    // Kullanıcıyı ReportPlayground rotasına (route) yönlendir.
    // Router'ımızın '/playground/:appId' gibi bir rotaya sahip olması gerekecek.
    navigate(`/nexus/playground/${app.id}`);
  };

  const renderContent = () => {
    if (isLoading) {
      return <Spinner />;
    }

    if (!dataApps || dataApps.length === 0) {
      return (
        <div className={styles.emptyState}>
          Rapor oluşturulabilecek aktif bir veri modeli bulunamadı.
          <br />
          Lütfen önce "Veri Modelleri" ekranından bir model oluşturun.
        </div>
      );
    }

    return (
      <ul className={styles.appList}>
        {dataApps.map(app => (
          <li key={app.id} className={styles.appItem}>
            <button onClick={() => handleSelectApp(app)} className={styles.appButton}>
              <div className={styles.appIcon}>
                <GitMerge size={24} />
              </div>
              <div className={styles.appInfo}>
                <span className={styles.appTitle}>{app.title}</span>
                <span className={styles.appConnection}>
                  Kaynak: {app.connection_display}
                </span>
              </div>
              <ChevronRight size={20} className={styles.appChevron} />
            </button>
          </li>
        ))}
      </ul>
    );
  };

  return (
    <Modal 
      isOpen={isOpen} 
      onClose={onClose} 
      title="Rapor için Bir Veri Modeli Seçin"
    >
      <div className={styles.modalContent}>
        <p className={styles.modalDescription}>
          Raporunuzu oluşturmak için temel alacağınız, önceden tanımlanmış bir veri modelini seçin.
        </p>
        {renderContent()}
      </div>
    </Modal>
  );
};

SelectDataAppModal.propTypes = {
  isOpen: PropTypes.bool.isRequired,
  onClose: PropTypes.func.isRequired,
};

export default SelectDataAppModal;