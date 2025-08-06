// path: frontend/src/components/formforgeapi/components/page-level/FormDataListScreen.jsx

import React, { useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import useFormForgeApi from '../../hooks/useFormForgeApi';
import DataTable from '../reusable/DataTable';
import ViewSubmissionModal from '../../utils/ViewSubmissionModal'; // Modal bileşenini import ediyoruz
import styles from '../../css/FormDataListScreen.module.css';

const FormDataListScreen = () => {
  const { formId } = useParams();

  // GÜNCELLEME: Hook'tan gelen değerler güncellendi
  const {
    currentForm,
    loading,
    error,
    fetchForm,
    fetchSubmissions,
    submissions, // Artık ham veri 'submissions' olarak geliyor
    submissionColumns,
    // Modal için yeni state ve handler'lar
    isViewModalOpen,
    setViewModalOpen,
    selectedSubmission,
  } = useFormForgeApi();

  useEffect(() => {
    if (formId) {
      // Hem formun üst bilgilerini (başlık vb.) hem de forma ait gönderimleri çekiyoruz.
      fetchForm(formId);
      fetchSubmissions(formId);
    }
    // `useCallback` kullandığımız için dependency'ler stabil.
  }, [formId, fetchForm, fetchSubmissions]);

  // Yükleme ve hata durumları için kullanıcı arayüzü
  if (loading && !currentForm) return <div>Veriler Yükleniyor...</div>;
  if (error) return <div className="alert alert-danger">Hata: {error}</div>;
  if (!currentForm) return <div>Form bilgisi bulunamadı.</div>;

  return (
    <div className={styles.formDataListScreen}>
      <div style={{ marginBottom: '1.5rem' }}>
        <Link to="/formforgeapi">&larr; Form Listesine Geri Dön</Link>
      </div>

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
          // GÜNCELLEME: DataTable'a artık formatlanmış veri yerine ham 'submissions' dizisini veriyoruz.
          // Sütunlardaki `accessor` fonksiyonları doğru veriyi kendileri bulacak.
          data={submissions}
        />
      </div>

      {/* YENİ: Modal'ı render etme */}
      {/* Sadece bir submission seçildiğinde (selectedSubmission dolu olduğunda) render edilecek. */}
      {selectedSubmission && (
        <ViewSubmissionModal
          isOpen={isViewModalOpen}
          onClose={() => setViewModalOpen(false)}
          submission={selectedSubmission}
        />
      )}
    </div>
  );
};

export default FormDataListScreen;