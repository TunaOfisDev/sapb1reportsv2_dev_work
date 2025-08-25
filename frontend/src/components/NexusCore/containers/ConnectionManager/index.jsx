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
  
  const { data: connections, loading, error, request: fetchConnections } = useApi(connectionsApi.getConnections);
  const { request: createConn } = useApi(connectionsApi.createConnection);
  const { request: updateConn } = useApi(connectionsApi.updateConnection);
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

  const handleOpenModalForEdit = (connection) => {
    setEditingConnection(connection);
    setIsModalOpen(true);
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
    addNotification('Bağlantı test ediliyor...', 'info'); // Kullanıcıya anında geri bildirim
    const { success, data, error } = await testConn(id);
    if (success) {
      addNotification(`Bağlantı testi başarılı: ${data.message}`, 'success');
    } else {
      const errorMessage = error?.response?.data?.error || 'Bağlantı testi başarısız oldu.';
      addNotification(errorMessage, 'error');
    }
  };

  const handleFormSubmit = async (formData) => {
    const apiCall = editingConnection 
      ? () => updateConn(editingConnection.id, formData)
      : () => createConn(formData);

    const { success, error } = await apiCall();
    
    if (success) {
      const message = editingConnection ? 'Bağlantı başarıyla güncellendi.' : 'Bağlantı başarıyla oluşturuldu.';
      addNotification(message, 'success');
      handleCloseModal();
      fetchConnections();
    } else {
      const errorMessage = error?.response?.data?.detail || 'İşlem sırasında bir hata oluştu.';
      addNotification(errorMessage, 'error');
    }
  };
  
  const renderContent = () => {
    if (loading && !connections) { // Sadece ilk yüklemede spinner göster
      return <Spinner />;
    }
    if (error) {
      return <p style={{ color: 'red', textAlign: 'center' }}>Veri kaynakları yüklenirken bir hata oluştu.</p>;
    }
    return (
      <ConnectionList 
        connections={connections || []}
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
        title={editingConnection ? 'Bağlantıyı Düzenle' : 'Yeni Veri Kaynağı Ekle'}
        isOpen={isModalOpen}
        onClose={handleCloseModal}
      >
        <ConnectionForm 
          onSubmit={handleFormSubmit}
          onCancel={handleCloseModal}
          initialData={editingConnection}
        />
      </Modal>
    </>
  );
};

export default ConnectionManager;