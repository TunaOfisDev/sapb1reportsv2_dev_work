// path: frontend/src/components/formforgeapi/components/page-level/FormDataListScreen.jsx

import React, { useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import useFormForgeApi from '../../hooks/useFormForgeApi';
import { useSubmissionColumns } from '../../hooks/useSubmissionColumns';
import DataTable from '../reusable/DataTable';
import ViewSubmissionModal from '../../utils/ViewSubmissionModal';
import styles from '../../css/FormDataListScreen.module.css';

const FormDataListScreen = () => {
  const { formId } = useParams();

  const {
    currentForm,
    loading,
    error,
    user,
    fetchForm,
    fetchSubmissions,
    submissions,
    isViewModalOpen,
    setViewModalOpen,
    selectedSubmission,
    actionHandlers
  } = useFormForgeApi();

  // Stil sınıflarını hook'a enjekte etmek için hazırlıyoruz.
  const columnClassNames = {
    cellContent: styles.formDataListScreen__cellContent,
    buttonInfo: `${styles.formDataListScreen__actionButton} ${styles.formDataListScreen__actionButton_info}`,
    buttonPrimary: `${styles.formDataListScreen__actionButton} ${styles.formDataListScreen__actionButton_primary}`,
  };

  const submissionColumns = useSubmissionColumns(currentForm, user, actionHandlers, columnClassNames);

  useEffect(() => {
    if (formId) {
      fetchForm(formId);
      fetchSubmissions(formId);
    }
  }, [formId, fetchForm, fetchSubmissions]);

  if (loading && !currentForm) return <div>Veriler Yükleniyor...</div>;
  if (error) return <div className="alert alert-danger">Hata: {error}</div>;
  if (!currentForm) return <div>Form bilgisi bulunamadı.</div>;

  return (
    <div className={styles.formDataListScreen}>
      {/* ... (Başlık ve diğer JSX kodları aynı) ... */}
      <div style={{ marginBottom: '1.5rem' }}>
        <Link to="/formforgeapi">&larr; Form Listesine Geri Dön</Link>
      </div>

      <div className={styles.formDataListScreen__header}>
        <h1 className={styles.formDataListScreen__title}>
          "{currentForm.title}" Formuna Ait Veriler
        </h1>
        <div className={styles.formDataListScreen__meta}>
          <span className={styles.meta__badge}>Versiyon: V{currentForm.version}</span>
          <span className={styles.meta__badge}>Durum: {currentForm.status_display}</span>
          {currentForm.parent_form && (
            <span className={styles.meta__badge}>(Ana Form ID: {currentForm.parent_form})</span>
          )}
        </div>
      </div>

      <div className={styles.formDataListScreen__table}>
        <DataTable columns={submissionColumns} data={submissions} />
      </div>

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