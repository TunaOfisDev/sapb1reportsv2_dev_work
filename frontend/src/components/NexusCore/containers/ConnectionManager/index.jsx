// path: frontend/src/components/NexusCore/containers/ConnectionManager/index.jsx
import React, { useState, useEffect } from 'react';
import { PlusCircle } from 'react-feather';

import Card from '../../components/common/Card/Card';
import Button from '../../components/common/Button/Button';
import Spinner from '../../components/common/Spinner/Spinner';
import Modal from '../../components/common/Modal/Modal';
import ConnectionList from './ConnectionList';
import ConnectionForm from './ConnectionForm';

import { useApi } from '../../hooks/useApi';
import { useNotifications } from '../../hooks/useNotifications';
import * as connectionsApi from '../../api/connectionsApi';

const ConnectionManager = () => {
  const { addNotification } = useNotifications();
  
  // API Hook'ları
  const { data: apiResponse, loading: isLoadingList, error, request: fetchConnections } = useApi(connectionsApi.getConnections);
  const { request: fetchConnectionById, loading: isLoadingDetails } = useApi(connectionsApi.getConnectionById);
  const { request: createConn, loading: isSaving } = useApi(connectionsApi.createConnection);
  const { request: updateConn, loading: isUpdating } = useApi(connectionsApi.updateConnection);
  const { request: deleteConn } = useApi(connectionsApi.deleteConnection);
  const { request: testConn } = useApi(connectionsApi.testConnection);

  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingConnection, setEditingConnection] = useState(null);

  useEffect(() => {
    fetchConnections();
  }, [fetchConnections]);

  const handleOpenModalForNew = () => {
    setEditingConnection(null);
    setIsModalOpen(true);
  };

  // ### MİMARİ GÜNCELLEME: "Düzenle" fonksiyonu artık asenkron ve API isteği atıyor ###
  const handleOpenModalForEdit = async (connection) => {
    setIsModalOpen(true);
    setEditingConnection(null); // Önceki veriyi temizle, spinner'ı göster

    // ID'yi kullanarak tam veriyi (config_json dahil) backend'den çek
    const { success, data } = await fetchConnectionById(connection.id);
    
    if (success) {
      // Tam veri geldiğinde, state'i güncelleyerek formun dolmasını sağla
      setEditingConnection(data);
    } else {
      addNotification('Bağlantı detayları alınırken bir hata oluştu.', 'error');
      handleCloseModal();
    }
  };

  const handleCloseModal = () => {
    setIsModalOpen(false);
    setEditingConnection(null);
  };

  const handleDelete = async (id) => {
    if (window.confirm('Bu bağlantıyı silmek istediğinizden emin misiniz?')) {
      const { success } = await deleteConn(id);
      if (success) {
        addNotification('Bağlantı başarıyla silindi.', 'success');
        fetchConnections();
      } else {
        addNotification('Bağlantı silinirken bir hata oluştu.', 'error');
      }
    }
  };
  
  const handleTest = async (id) => {
    addNotification('Bağlantı test ediliyor...', 'info');
    const { success, data, error } = await testConn(id);
    if (success) {
      addNotification(`Bağlantı testi başarılı: ${data.message}`, 'success');
    } else {
      const errorMessage = error?.response?.data?.message || 'Bağlantı testi başarısız oldu.';
      addNotification(errorMessage, 'error');
    }
  };

  const handleFormSubmit = async (formData) => {
    const apiCall = editingConnection?.id 
      ? () => updateConn(editingConnection.id, formData)
      : () => createConn(formData);

    const { success, error } = await apiCall();
    
    if (success) {
      const message = editingConnection?.id ? 'Bağlantı başarıyla güncellendi.' : 'Bağlantı başarıyla oluşturuldu.';
      addNotification(message, 'success');
      handleCloseModal();
      fetchConnections();
    } else {
      // Backend'den gelen spesifik hata mesajını gösterelim
      const errorMessage = error?.response?.data?.config_json?.[0] || error?.response?.data?.detail || 'İşlem sırasında bir hata oluştu.';
      addNotification(errorMessage, 'error');
    }
  };
  
  const renderContent = () => {
    if (isLoadingList && !apiResponse) {
      return <Spinner />;
    }
    if (error) {
      return <p style={{ color: 'red', textAlign: 'center' }}>Veri kaynakları yüklenirken bir hata oluştu.</p>;
    }
    
    return (
      <ConnectionList 
        connections={apiResponse?.results || []}
        onEdit={handleOpenModalForEdit}
        onDelete={handleDelete}
        onTest={handleTest}
      />
    );
  };

  return (
    <>
      <Card
        title="Veri Kaynağı Yöneticisi"
        headerActions={
          <Button onClick={handleOpenModalForNew} IconComponent={PlusCircle}>
            Yeni Bağlantı Ekle
          </Button>
        }
      >
        {renderContent()}
      </Card>

      <Modal
        title={editingConnection?.title ? `Düzenle: ${editingConnection.title}` : 'Yeni Veri Kaynağı Ekle'}
        isOpen={isModalOpen}
        onClose={handleCloseModal}
      >
        {/* ### MİMARİ GÜNCELLEME: Detaylar yüklenirken Spinner gösterilir ### */}
        {isLoadingDetails ? (
            <Spinner />
        ) : (
            <ConnectionForm 
              onSubmit={handleFormSubmit}
              onCancel={handleCloseModal}
              initialData={editingConnection}
              isSaving={isSaving || isUpdating}
            />
        )}
      </Modal>
    </>
  );
};

export default ConnectionManager;