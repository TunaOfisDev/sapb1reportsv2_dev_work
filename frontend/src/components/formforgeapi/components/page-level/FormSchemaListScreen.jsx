// path: frontend/src/components/formforgeapi/components/page-level/FormSchemaListScreen.jsx
import React, { useEffect, useMemo } from 'react';
import { Link } from 'react-router-dom';
import useFormForgeApi from '../../hooks/useFormForgeApi';
import DataTable from '../reusable/DataTable';
import styles from '../../css/FormSchemaListScreen.module.css';

const FormSchemaListScreen = () => {
  const { forms, loading, error, fetchForms, deleteForm } = useFormForgeApi();

  useEffect(() => {
    fetchForms();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const handleDelete = (formId) => {
    if (window.confirm("Bu formu ve ilişkili tüm verileri silmek istediğinizden emin misiniz? Bu işlem geri alınamaz.")) {
      deleteForm(formId);
    }
  };

  const columns = useMemo(
    () => [
      {
        Header: 'Form Başlığı',
        accessor: 'title',
      },
      {
        Header: 'Departman',
        accessor: 'department_name',
      },
      {
        Header: 'Oluşturan (ID)',
        accessor: 'created_by',
      },
      {
        Header: 'Tarih',
        accessor: 'created_at',
        Cell: ({ value }) => new Date(value).toLocaleDateString(),
      },
      {
        Header: 'Eylemler',
        id: 'actions',
        Cell: ({ row }) => (
          <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
            {/* DEĞİŞİKLİK: "Paylaş" butonu yerine "Veri Gir" linki eklendi */}
            <Link 
              to={`fill/${row.original.id}`} 
              className="btn btn-sm btn-outline-success"
              title="Bu Forma Veri Gir"
            >
              Veri Gir
            </Link>
            
            <Link to={`builder/${row.original.id}`} className="btn btn-sm btn-outline-primary">
              Düzenle
            </Link>
            <Link to={`data/${row.original.id}`} className="btn btn-sm btn-outline-secondary">
              Veriler
            </Link>
            <button
              onClick={() => handleDelete(row.original.id)}
              className="btn btn-sm btn-outline-danger"
            >
              Sil
            </button>
          </div>
        ),
      },
    ],
    []
  );

  if (loading) return <div>Yükleniyor...</div>;
  if (error) return <div className="alert alert-danger">Hata: {error}</div>;

  return (
    <div className={styles.formSchemaListScreen}>
      <div className={styles.formSchemaListScreen__header}>
        <h1 className={styles.formSchemaListScreen__title}>Form Şemaları</h1>
        <Link to="builder/new" className={styles.formSchemaListScreen__newBtn}>
          + Yeni Form Oluştur
        </Link>
      </div>

      <div className={styles.formSchemaListScreen__table}>
        <DataTable columns={columns} data={forms} />
      </div>
    </div>
  );
};

export default FormSchemaListScreen;