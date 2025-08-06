// path: frontend/src/components/formforgeapi/components/page-level/FormSchemaListScreen.jsx

import React, { useEffect, useMemo, useState } from 'react';
import { Link } from 'react-router-dom';
import useFormForgeApi from '../../hooks/useFormForgeApi';
import DataTable from '../reusable/DataTable';
import styles from '../../css/FormSchemaListScreen.module.css';

const FormSchemaListScreen = () => {
  // YENİ: Hangi listenin gösterileceğini tutan state (aktif mi, arşiv mi?)
  const [showArchived, setShowArchived] = useState(false);
  
  // GÜNCELLENDİ: Hook'tan yeni state ve fonksiyonları alıyoruz
  const { 
    forms, 
    archivedForms, 
    loading, 
    error, 
    fetchForms, 
    archiveForm, 
    unarchiveForm,
    createNewVersion 
  } = useFormForgeApi();

  useEffect(() => {
    // State'e göre ya aktif ya da arşivlenmiş formları çekiyoruz
    const statusToFetch = showArchived ? 'ARCHIVED' : 'PUBLISHED';
    fetchForms(statusToFetch);
  }, [showArchived, fetchForms]);

  const handleArchive = (formId) => {
    if (window.confirm("Bu formu arşive kaldırmak istediğinizden emin misiniz? Arşivden geri alınamaz.")) {
      archiveForm(formId);
    }
  };

  // YENİ: Arşivden çıkarma butonu için handle fonksiyonu
  const handleUnarchive = (formId) => {
    if (window.confirm("Bu form arşivden çıkarılıp tekrar aktif formlar listesine eklenecektir. Onaylıyor musunuz?")) {
      unarchiveForm(formId);
    }
  };


  const handleEdit = (formId) => {
    if (window.confirm("Bu formu düzenlemek için yeni bir versiyon oluşturulacaktır. Mevcut versiyon arşivlenecektir. Onaylıyor musunuz?")) {
      createNewVersion(formId);
    }
  };

  const columns = useMemo(
    () => [
      {
        Header: 'Form Başlığı',
        accessor: 'title',
      },
      // YENİ: Versiyon ve Durum sütunları eklendi
      {
        Header: 'Versiyon',
        accessor: 'version',
        Cell: ({ value }) => `V${value}`,
      },
      {
        Header: 'Durum',
        accessor: 'status_display',
      },
      {
        Header: 'Departman',
        accessor: 'department_name',
      },
      {
        Header: 'Eylemler',
        id: 'actions',
        Cell: ({ row }) => (
          <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
            {/* Arşivdeki formlar için sadece Veriler butonu aktif */}
            {showArchived ? (
              // Arşiv görünümündeki butonlar
              <>
                {/* YENİ BUTON */}
                <button onClick={() => handleUnarchive(row.original.id)} className="btn btn-sm btn-outline-success">Yeniden Yayınla</button>
                <Link to={`data/${row.original.id}`} className="btn btn-sm btn-outline-secondary">Verileri Görüntüle</Link>
              </>
            ) : (
              // Aktif formlar görünümündeki butonlar (değişiklik yok)
              <>
                <Link to={`fill/${row.original.id}`} className="btn btn-sm btn-outline-success">Veri Gir</Link>
                <button onClick={() => handleEdit(row.original.id)} className="btn btn-sm btn-outline-primary">Düzenle</button>
                <Link to={`data/${row.original.id}`} className="btn btn-sm btn-outline-secondary">Veriler</Link>
                <button onClick={() => handleArchive(row.original.id)} className="btn btn-sm btn-outline-warning">Arşivle</button>
              </>
            )}
            
            {/* TODO: Bu buton tıklandığında versiyonları listeleyen bir modal açılabilir */}
            <button className="btn btn-sm btn-outline-info" disabled title={row.original.versions?.join('\n') || 'Geçmiş versiyon yok'}>
              Versiyonlar ({row.original.versions?.length || 0})
            </button>
          </div>
        ),
      },
    ],
    // showArchived state'i değiştiğinde kolonların yeniden render edilmesi için dependency'e eklendi
    [showArchived, handleArchive, handleEdit, handleUnarchive]
  );

  const dataToDisplay = showArchived ? archivedForms : forms;

  if (loading && dataToDisplay.length === 0) return <div>Yükleniyor...</div>;
  if (error) return <div className="alert alert-danger">Hata: {error}</div>;

  return (
    <div className={styles.formSchemaListScreen}>
      <div className={styles.formSchemaListScreen__header}>
        <h1 className={styles.formSchemaListScreen__title}>
          {showArchived ? "Arşivlenmiş Formlar" : "Aktif Form Şemaları"}
        </h1>
        <div>
            {/* YENİ: Arşiv ve Aktif formlar arasında geçiş butonu */}
            <button onClick={() => setShowArchived(!showArchived)} className="btn btn-secondary me-2">
                {showArchived ? "Aktif Formları Göster" : "Arşivi Göster"}
            </button>
            <Link to="builder/new" className={styles.formSchemaListScreen__newBtn}>
                + Yeni Form Oluştur
            </Link>
        </div>
      </div>

      <div className={styles.formSchemaListScreen__table}>
        <DataTable columns={columns} data={dataToDisplay} />
      </div>
    </div>
  );
};

export default FormSchemaListScreen;