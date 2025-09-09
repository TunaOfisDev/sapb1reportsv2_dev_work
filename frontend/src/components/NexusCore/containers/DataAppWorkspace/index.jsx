// path: frontend/src/components/NexusCore/containers/DataAppWorkspace/index.jsx

import React, { useEffect, useState, useCallback } from 'react';
import { Plus, Edit, Trash2 } from 'react-feather';
import { useDataApps } from '../../hooks/useDataApps'; // ANA HOOK'UMUZU IMPORT EDİYORUZ
import PageWrapper from '../../components/layout/PageWrapper/PageWrapper';
import Button from '../../components/common/Button/Button';
import Table from '../../components/common/Table/Table';
import Modal from '../../components/common/Modal/Modal';
import Spinner from '../../components/common/Spinner/Spinner';
import { formatRelativeTime } from '../../utils/formatters'; // Tarih formatlayıcımızı import edelim
import styles from './DataAppWorkspace.module.scss'; 

// TODO: Bu formu bir sonraki adımda oluşturacağız.
// import DataAppForm from './DataAppForm'; 

/**
 * Veri Modellerini (DataApp) yönetmek için ana konteyner bileşeni.
 * Tüm CRUD mantığı 'useDataApps' hook'u tarafından sağlanır.
 */
const DataAppWorkspace = () => {
  // 1. Hook'u çağırarak tüm state mantığını alıyoruz.
  const { 
    dataApps, 
    isLoading, 
    loadDataApps, 
    deleteApp, 
    isDeleting 
  } = useDataApps();

  // 2. Modal (Yeni/Düzenle Formu) state yönetimi
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingApp, setEditingApp] = useState(null); // null ise 'Yeni', dolu ise 'Düzenle' modudur

  // 3. Bileşen yüklendiğinde verileri çekmek için Effect
  useEffect(() => {
    loadDataApps();
  }, [loadDataApps]); // loadDataApps, hook içinde useCallback ile sarmalandığı için stabildir.

  // --- Eylem Handler'ları ---

  const handleOpenCreateModal = () => {
    setEditingApp(null); // Düzenleme modunu temizle
    setIsModalOpen(true);
  };

  const handleOpenEditModal = (app) => {
    setEditingApp(app); // Düzenlenecek uygulamayı ayarla
    setIsModalOpen(true);
  };

  const handleCloseModal = () => {
    setIsModalOpen(false);
    setEditingApp(null);
  };

  const handleSaveSuccess = () => {
    // Form başarıyla kaydedildiğinde (hook zaten listeyi yeniledi),
    // tek yapmamız gereken modal'ı kapatmak.
    handleCloseModal();
  };

  const handleDelete = async (id) => {
    // Silme işlemi (confirm penceresi dahil) hook içinde hallediliyor.
    await deleteApp(id);
  };

  // 4. Tablo kolonlarını tanımlama
  const columns = React.useMemo(() => [
    {
      header: 'Model Başlığı',
      accessor: 'title',
      cell: (title, row) => (
        <div>
          <div className={styles.tableTitle}>{title}</div>
          <div className={styles.tableDescription}>{row.description || 'Açıklama yok'}</div>
        </div>
      )
    },
    {
      header: 'Veri Kaynağı',
      accessor: 'connection_display', // Serializer'dan gelen okunabilir isim
    },
    {
      header: 'Sahip',
      accessor: 'owner', // Serializer'dan gelen email
    },
    {
      header: 'Son Güncelleme',
      accessor: 'updated_at',
      cell: (date) => formatRelativeTime(date) // Tarihi "3 saat önce" gibi formatla
    },
    {
      header: 'Eylemler',
      accessor: 'id',
      cell: (id, row) => (
        <div className={styles.actionButtons}>
          <Button 
            onClick={() => handleOpenEditModal(row)} 
            variant="icon" 
            aria-label="Düzenle"
            tooltip="Veri Modelini Düzenle"
          >
            <Edit size={18} />
          </Button>
          <Button 
            onClick={() => handleDelete(id)} 
            variant="icon" 
            danger 
            aria-label="Sil"
            tooltip="Sil"
            disabled={isDeleting} // Silme işlemi sürerken butonu kilitle
          >
            <Trash2 size={18} />
          </Button>
        </div>
      )
    }
  ], [isDeleting]); // isDeleting değiştiğinde butonun durumunu güncellemek için


  // 5. Render
  return (
    <PageWrapper title="Veri Modelleri" (DataApp Workspace)>
      <div className={styles.workspaceHeader}>
        <p className={styles.pageDescription}>
          Ham sorguları (Sanal Tablolar) birleştirip aralarında ilişkiler (JOINs) kurarak
          raporlamaya hazır veri modelleri oluşturun.
        </p>
        <Button 
          onClick={handleOpenCreateModal} 
          variant="primary"
          icon={<Plus size={18} />}
        >
          Yeni Veri Modeli
        </Button>
      </div>

      {isLoading && <Spinner />}

      {!isLoading && dataApps.length === 0 && (
        <div className={styles.emptyState}>
          Henüz hiç veri modeli oluşturulmamış. Başlamak için "Yeni Veri Modeli" butonuna tıklayın.
        </div>
      )}

      {!isLoading && dataApps.length > 0 && (
        <Table columns={columns} data={dataApps} />
      )}

      {/* YENİ / DÜZENLEME MODALI */}
      <Modal 
        isOpen={isModalOpen} 
        onClose={handleCloseModal} 
        title={editingApp ? "Veri Modelini Düzenle" : "Yeni Veri Modeli Oluştur"}
      >
        {/* BİR SONRAKİ ADIMIMIZ: Bu modalın içini dolduracak olan 
            DataAppForm bileşenini buraya yerleştireceğiz. */}
        
        <div>
           <h4>(Faz 1, Madde 4: DataAppForm buraya gelecek)</h4>
           <p>Mevcut App: {editingApp ? editingApp.title : 'Yok'}</p>
           <Button onClick={handleSaveSuccess}>Geçici Kaydet/Kapat</Button>
        </div>
        
        {/* <DataAppForm 
          existingApp={editingApp} 
          onSaveSuccess={handleSaveSuccess}
          onCancel={handleCloseModal}
        /> 
        */}
      </Modal>

    </PageWrapper>
  );
};

export default DataAppWorkspace;