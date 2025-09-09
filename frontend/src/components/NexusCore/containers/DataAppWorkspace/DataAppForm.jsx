// path: frontend/src/components/NexusCore/containers/DataAppWorkspace/DataAppForm.jsx

import React, { useState, useEffect, useMemo } from 'react';
import PropTypes from 'prop-types';
import { useDataApps } from '../../hooks/useDataApps';
import { useAppRelationships } from '../../hooks/useAppRelationships';
import { useApi } from '../../hooks/useApi';
import * as connectionsApi from '../../api/connectionsApi';
import * as virtualTablesApi from '../../api/virtualTablesApi';

import Input from '../../components/common/Input/Input';
import Textarea from '../../components/common/Textarea/Textarea';
import Select from '../../components/common/Select/Select';
import Button from '../../components/common/Button/Button';
import Spinner from '../../components/common/Spinner/Spinner';
import { Edit, Plus, Trash2, GitMerge } from 'react-feather';
import styles from './DataAppForm.module.scss';

/**
 * Bu bileşen, DataApp yaratma ve düzenleme sihirbazının tamamını yönetir.
 * 3 Sekmeli bir mantık kullanır: Genel -> Tablolar -> İlişkiler.
 */
const DataAppForm = ({ existingApp, onSaveSuccess, onCancel }) => {
  const [currentApp, setCurrentApp] = useState(existingApp || null);
  const isNewApp = !currentApp;
  const [activeTab, setActiveTab] = useState('general'); // 'general', 'tables', 'relationships'

  // --- 1. Form State'leri ---
  // A. Genel Sekmesi State'i
  const [generalData, setGeneralData] = useState({
    title: existingApp?.title || '',
    description: existingApp?.description || '',
    connection_id: existingApp?.connection || '', // Sadece ID'yi tutarız
  });

  // B. Tablo Seçimi Sekmesi State'i
  // ManyToMany alanı sadece ID'lerin bir dizisidir.
  const [selectedTableIds, setSelectedTableIds] = useState(existingApp?.virtual_tables || []);

  // C. İlişki Sekmesi State'i (Yeni ilişki formu için)
  const [newRel, setNewRel] = useState({
    left_table: '',
    left_column: '',
    right_table: '',
    right_column: '',
    join_type: 'LEFT JOIN',
  });

  // --- 2. Gerekli Verileri Çekmek için Hook'lar ---
  // A. Formdaki 'DataApp' CRUD işlemleri için ana hook'umuz
  // (Listeye değil, sadece eylem fonksiyonlarına ihtiyacımız var)
  const { createApp, updateApp, isCreating, isUpdating } = useDataApps();
  
  // B. Bağlantı listesini (Connection dropdown) doldurmak için
  const connectionsHook = useApi(connectionsApi.getConnections);
  
  // C. Sanal Tablo listesini (Table selector) doldurmak için
  const tablesHook = useApi(virtualTablesApi.getVirtualTables);

  // D. İlişki (Relationship) CRUD işlemleri için hook
  // Bu hook, 'currentApp' güncellendiğinde tetiklenecek olan parent'ın 
  // (DataAppWorkspace) listesini yenilemesi için 'onSaveSuccess'i çağırır.
  const relsHook = useAppRelationships(onSaveSuccess); 

  // --- 3. Veri Yükleme Effect'leri ---
  // Component yüklendiğinde, form için gerekli olan master datayı (Connections ve VTables) çek.
  useEffect(() => {
    connectionsHook.request();
    tablesHook.request();
  }, []); // Sadece bir kez çalışır

  // --- 4. Filtrelenmiş/Hesaplanmış Değerler (Memos) ---
  
  // A. Sadece seçili bağlantıya ait olan Sanal Tabloları göster
  const availableTablesForConnection = useMemo(() => {
    const allTables = tablesHook.data?.results || tablesHook.data || [];
    if (!generalData.connection_id) return [];
    return allTables.filter(vt => vt.connection === parseInt(generalData.connection_id));
  }, [tablesHook.data, generalData.connection_id]);

  // B. Sadece seçilmiş ve kaydedilmiş tablolara (DataApp'in M2M listesi) ait tam nesneleri al.
  // Bu, İlişki Editörü'ndeki dropdown'ları doldurmak için kullanılır.
  const tablesSelectedInApp = useMemo(() => {
    const allTables = tablesHook.data?.results || tablesHook.data || [];
    return allTables.filter(vt => selectedTableIds.includes(vt.id));
  }, [tablesHook.data, selectedTableIds]);

  // C. Sadece bu App'e ait olan ilişkileri göster
  const relationshipsForThisApp = useMemo(() => {
    return relsHook.relationships.filter(rel => rel.app === currentApp?.id);
  }, [relsHook.relationships, currentApp?.id]);

  // App yüklendiğinde ilişkileri de yükle
  useEffect(() => {
    if (currentApp?.id) {
      relsHook.loadRelationships();
    }
  }, [currentApp?.id, relsHook.loadRelationships]);

  // --- 5. Eylem (Action) Handler'ları ---

  const handleGeneralChange = (e) => {
    const { name, value } = e.target;
    setGeneralData(prev => ({ ...prev, [name]: value }));
  };

  const handleTableSelectionChange = (tableId) => {
    setSelectedTableIds(prevIds => 
      prevIds.includes(tableId)
        ? prevIds.filter(id => id !== tableId) // Varsa çıkar (uncheck)
        : [...prevIds, tableId] // Yoksa ekle (check)
    );
  };

  const handleNewRelChange = (e) => {
    const { name, value } = e.target;
    setNewRel(prev => ({ ...prev, [name]: value }));
  };

  // ADIM 1: YENİ UYGULAMA YARATMA
  const handleCreateApp = async () => {
    const payload = { 
      ...generalData, 
      virtual_tables: selectedTableIds // İlk yaratılışta tablo da gönderebiliriz
    };
    const { success, data } = await createApp(payload);
    if (success) {
      setCurrentApp(data); // App nesnesini state'e al
      setIsModalOpen(false); // Modal'ı kapat (veya diğer sekmeye geç)
      setActiveTab('tables'); // Otomatik olarak 2. sekmeye geç
      onSaveSuccess(); // Ana liste sayfasını yenile
    }
  };

  // ADIM 2: MEVCUT UYGULAMAYI GÜNCELLEME (Genel veya Tablolar)
  const handleUpdateApp = async () => {
    const payload = {
      title: generalData.title,
      description: generalData.description,
      virtual_tables: selectedTableIds // Güncel tablo listesini yolla
    };
    const { success, data } = await updateApp(currentApp.id, payload);
    if (success) {
      setCurrentApp(data); // Güncel app verisini state'e al
      onSaveSuccess(); // Ana listeyi yenile
    }
    // Bu 'update' işlemi modal'ı kapatmaz, kullanıcı sekmelerde gezmeye devam edebilir.
  };

  // ADIM 3: İLİŞKİ YARATMA
  const handleCreateRelationship = async () => {
    const payload = {
      ...newRel,
      app: currentApp.id // Bu ilişkiyi mevcut App'e bağla
    };
    await relsHook.createRelationship(payload);
    // Formu temizle
    setNewRel({ left_table: '', left_column: '', right_table: '', right_column: '', join_type: 'LEFT JOIN' });
  };


  const renderLoading = () => <div className={styles.fullLoader}><Spinner /></div>;
  const isFormLoading = connectionsHook.loading || tablesHook.loading;

  // --- 6. Render Fonksiyonları (Sekmeler için) ---

  const renderGeneralTab = () => (
    <div className={styles.tabContent}>
      <Input
        label="Veri Modeli Başlığı"
        name="title"
        value={generalData.title}
        onChange={handleGeneralChange}
        placeholder="Örn: Aylık Satış Veri Modeli"
        required
      />
      <Textarea
        label="Açıklama"
        name="description"
        value={generalData.description}
        onChange={handleGeneralChange}
        rows={3}
      />
      <Select
        label="Veri Kaynağı"
        name="connection_id"
        value={generalData.connection_id}
        onChange={handleGeneralChange}
        disabled={!isNewApp || connectionsHook.loading} // Yaratıldıktan sonra BAĞLANTI DEĞİŞTİRİLEMEZ.
        required
      >
        <option value="">Bir veri kaynağı seçin...</option>
        {(connectionsHook.data || []).map(conn => (
          <option key={conn.id} value={conn.id}>{conn.title}</option>
        ))}
      </Select>
      {!isNewApp && (
         <p className={styles.helpText}>Bir veri modelinin ana bağlantısı oluşturulduktan sonra değiştirilemez.</p>
      )}
      <div className={styles.formActions}>
        <Button onClick={isNewApp ? handleCreateApp : handleUpdateApp} variant="primary" disabled={isCreating || isUpdating}>
          {isNewApp ? 'Oluştur ve Tabloları Seç' : 'Genel Bilgileri Güncelle'}
        </Button>
      </div>
    </div>
  );

  const renderTablesTab = () => (
    <div className={styles.tabContent}>
      <div className={styles.tableSelector}>
        <h4>Modelde Kullanılacak Tablolar</h4>
        <p className={styles.helpText}>Sadece seçtiğiniz '{generalData.connection_id}' kaynağına ait tablolar listelenir.</p>
        <div className={styles.checkboxList}>
          {availableTablesForConnection.length === 0 && <p>Bu kaynak için sanal tablo bulunamadı.</p>}
          {availableTablesForConnection.map(vt => (
            <label key={vt.id} className={styles.checkboxLabel}>
              <input 
                type="checkbox"
                checked={selectedTableIds.includes(vt.id)}
                onChange={() => handleTableSelectionChange(vt.id)}
              />
              {vt.title}
            </label>
          ))}
        </div>
      </div>
      <div className={styles.formActions}>
        <Button onClick={handleUpdateApp} variant="primary" disabled={isUpdating}>
          Tablo Seçimini Kaydet
        </Button>
      </div>
    </div>
  );

  const renderRelationshipsTab = () => (
    <div className={styles.tabContent}>
        {/* A. YENİ İLİŞKİ FORMU */}
        <div className={styles.relForm}>
            <GitMerge size={18} /> <h4>Yeni İlişki (JOIN) Ekle</h4>
        </div>
        <p className={styles.helpText}>Modelinize eklediğiniz tablolar arasında JOIN bağlantıları oluşturun.</p>

        <div className={styles.relFormGrid}>
          <Select name="left_table" value={newRel.left_table} onChange={handleNewRelChange}>
              <option value="">Sol Tablo Seç...</option>
              {tablesSelectedInApp.map(t => <option key={t.id} value={t.id}>{t.title}</option>)}
          </Select>
          <Input name="left_column" value={newRel.left_column} onChange={handleNewRelChange} placeholder="Sol Kolon Adı (örn: MusteriID)" />
          <Select name="right_table" value={newRel.right_table} onChange={handleNewRelChange}>
              <option value="">Sağ Tablo Seç...</option>
              {tablesSelectedInApp.map(t => <option key={t.id} value={t.id}>{t.title}</option>)}
          </Select>
          <Input name="right_column" value={newRel.right_column} onChange={handleNewRelChange} placeholder="Sağ Kolon Adı (örn: ID)" />
          <Select name="join_type" value={newRel.join_type} onChange={handleNewRelChange}>
              <option value="LEFT JOIN">LEFT JOIN</option>
              <option value="INNER JOIN">INNER JOIN</option>
          </Select>
          <Button onClick={handleCreateRelationship} variant="primary" disabled={relsHook.isCreating}>
              <Plus size={16} /> Ekle
          </Button>
        </div>

        <hr className={styles.divider} />

        {/* B. MEVCUT İLİŞKİLER LİSTESİ */}
        <h4>Tanımlı İlişkiler</h4>
        <div className={styles.relList}>
            {relsHook.isLoading && <Spinner size="small" />}
            {relationshipsForThisApp.length === 0 && !relsHook.isLoading && <p>Henüz ilişki tanımlanmamış.</p>}
            {relationshipsForThisApp.map(rel => (
                <div key={rel.id} className={styles.relItem}>
                    <span>
                      <strong>{rel.left_table_display}</strong>.{rel.left_column}
                    </span>
                    <span className={styles.relType}>({rel.join_type_display})</span>
                    <span>
                      <strong>{rel.right_table_display}</strong>.{rel.right_column}
                    </span>
                    <Button 
                        onClick={() => relsHook.deleteRelationship(rel.id)}
                        variant="icon" danger disabled={relsHook.isDeleting}>
                        <Trash2 size={16} />
                    </Button>
                </div>
            ))}
        </div>
    </div>
  );

  return (
    <div className={styles.formContainer}>
      {isFormLoading && renderLoading()}
      
      <nav className={styles.tabNav}>
        <button 
          className={`${styles.tabButton} ${activeTab === 'general' ? styles.active : ''}`}
          onClick={() => setActiveTab('general')}
        >
          1. Genel Bilgiler
        </button>
        <button 
          className={`${styles.tabButton} ${activeTab === 'tables' ? styles.active : ''}`}
          onClick={() => setActiveTab('tables')}
          disabled={isNewApp} // App yaratılmadan bu sekmeler açılamaz
        >
          2. Veri Kümeleri
        </button>
        <button 
          className={`${styles.tabButton} ${activeTab === 'relationships' ? styles.active : ''}`}
          onClick={() => setActiveTab('relationships')}
          disabled={isNewApp} // App yaratılmadan bu sekmeler açılamaz
        >
          3. İlişkiler (JOINs)
        </button>
      </nav>

      <div className={styles.tabPanel}>
          {activeTab === 'general' && renderGeneralTab()}
          {activeTab === 'tables' && !isNewApp && renderTablesTab()}
          {activeTab === 'relationships' && !isNewApp && renderRelationshipsTab()}
      </div>

      <div className={styles.modalFooter}>
          <Button onClick={onCancel} variant="default">
              Kapat
          </Button>
      </div>
    </div>
  );
};

DataAppForm.propTypes = {
  existingApp: PropTypes.object, // 'null' ise Yeni Kayıt modundadır
  onSaveSuccess: PropTypes.func.isRequired,
  onCancel: PropTypes.func.isRequired,
};

export default DataAppForm;