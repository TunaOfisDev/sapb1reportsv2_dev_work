// path: frontend/src/components/formforgeapi/components/page-level/FormDataListScreen.jsx

import React, { useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import useFormForgeApi from '../../hooks/useFormForgeApi';
import DataTable from '../reusable/DataTable';
import styles from '../../css/FormDataListScreen.module.css';

const FormDataListScreen = () => {
  const { formId } = useParams();
  const {
    currentForm,
    loading,
    error,
    fetchForm,
    fetchSubmissions,
    submissionColumns,
    submissionFormattedData
  } = useFormForgeApi();

  useEffect(() => {
    if (formId) {
      // Hem formun detaylarını (başlık, versiyon vb. için)
      // hem de bu forma ait gönderimleri çekiyoruz.
      fetchForm(formId);
      fetchSubmissions(formId);
    }
  }, [formId, fetchForm, fetchSubmissions]);

  if (loading && !currentForm) return <div>Veriler Yükleniyor...</div>;
  if (error) return <div className="alert alert-danger">Hata: {error}</div>;
  if (!currentForm) return <div>Form bilgisi bulunamadı.</div>;

  return (
    <div className={styles.formDataListScreen}>
      <div style={{ marginBottom: '1.5rem' }}>
        {/* GÜNCELLENDİ: "Arşiv" sekmesinden gelindiyse oraya geri dönmek mantıklı olabilir. 
            Şimdilik ana listeye dönüyoruz. */}
        <Link to="/formforgeapi">&larr; Form Listesine Geri Dön</Link>
      </div>

      {/* GÜNCELLENDİ: Başlığa formun versiyon ve durum bilgisi eklendi */}
      <div className={styles.formDataListScreen__header}>
        <h1 className={styles.formDataListScreen__title}>
          "{currentForm.title}" Formuna Ait Veriler
        </h1>
        <div className={styles.formDataListScreen__meta}>
          <span className={styles.meta__badge}>
            Versiyon: V{currentForm.version}
          </span>
          <span className={styles.meta__badge}>
            Durum: {currentForm.status_display}
          </span>
          {currentForm.parent_form && (
            <span className={styles.meta__badge}>
              (Ana Form ID: {currentForm.parent_form})
            </span>
          )}
        </div>
      </div>

      <div className={styles.formDataListScreen__table}>
        <DataTable
          columns={submissionColumns}
          data={submissionFormattedData}
        />
      </div>
    </div>
  );
};

export default FormDataListScreen;