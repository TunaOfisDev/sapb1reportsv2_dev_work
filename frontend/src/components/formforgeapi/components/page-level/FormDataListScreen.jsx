// path: frontend/src/components/formforgeapi/components/page-level/FormDataListScreen.jsx
import React, { useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import useFormForgeApi from '../../hooks/useFormForgeApi';
import DataTable from '../reusable/DataTable';
import styles from '../../css/FormDataListScreen.module.css';

/**
 * FormDataListScreen Bileşeni
 * --------------------------------------------------------------------
 * Belirli bir forma ait gönderilmiş tüm verileri bir tabloda listeler.
 *
 * Mimarideki Yeri:
 * - "Aptal" bir sayfa bileşenidir.
 * - Gerekli tüm veriyi ve mantığı (`currentForm`, `submissions`, `submissionColumns`,
 * `submissionFormattedData`) `useFormForgeApi` hook'undan alır.
 * - Bileşen yüklendiğinde, hem form şemasını (sütunlar için) hem de
 * gönderimleri (`submissions`) getirmek için hook'u tetikler.
 *
 * İş Akışı:
 * 1. URL'den `formId` alınır.
 * 2. `useEffect` ile `fetchForm(formId)` ve `fetchSubmissions(formId)` çağrılır.
 * 3. Hook, bu verileri işleyerek dinamik sütunları ve formatlanmış veriyi hazırlar.
 * 4. Bu hazır veriler, `DataTable` bileşenine `columns` ve `data` propları
 * olarak geçirilir.
 */
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
      fetchForm(formId);
      fetchSubmissions(formId);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [formId]);

  if (loading && !currentForm) return <div>Veriler Yükleniyor...</div>;
  if (error) return <div className="alert alert-danger">Hata: {error}</div>;
  if (!currentForm) return <div>Form bilgisi bulunamadı.</div>;

  return (
    <div className={styles.formDataListScreen}>
      <div style={{ marginBottom: '1rem' }}>
        <Link to="/formforgeapi/forms">&larr; Form Listesine Geri Dön</Link>
      </div>
      <h1 className={styles.formDataListScreen__title}>
        "{currentForm.title}" Formuna Ait Veriler
      </h1>

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