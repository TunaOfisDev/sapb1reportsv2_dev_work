// path: frontend/src/components/formforgeapi/components/page-level/FormDataListScreen.jsx
import React, { useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';

// Custom Hooks
import useFormForgeApi from '../../hooks/useFormForgeApi';
import { useHistoryFormForgeApi } from '../../hooks/useHistoryFormForgeApi';
import { useSubmissionColumns } from '../../hooks/useSubmissionColumns';

// Reusable & Utility Components
import DataTable from '../reusable/DataTable';
import ViewSubmissionModal from '../../utils/ViewSubmissionModal';
import UpdateSubmissionModal from '../../utils/UpdateSubmissionModal';
import SubmissionHistoryModal from '../../utils/SubmissionHistoryModal';

// Styles
import styles from '../../css/FormDataListScreen.module.css';

const FormDataListScreen = () => {
    const { formId } = useParams();

    // 1. Ana veri ve eylem yönetimi için hook (form listesi, güncelleme vb.)
    const {
        currentForm, loading: formLoading, error: formError, user,
        fetchForm, fetchSubmissions, submissions, updateSubmission,
        isViewModalOpen, setViewModalOpen, selectedSubmission,
        isUpdateModalOpen, setUpdateModalOpen, submissionToEdit,
        actionHandlers: formActionHandlers,
    } = useFormForgeApi();

    // 2. Sadece gönderi geçmişi modalının mantığı için ayrılmış hook
    const {
        isHistoryModalOpen, submissionHistory, selectedSubmission: selectedSubmissionForHistory,
        openHistoryModal, closeHistoryModal, isLoading: historyLoading,
    } = useHistoryFormForgeApi();

    // İki hook'tan gelen eylem handler'larını birleştiriyoruz.
    const allActionHandlers = {
        ...formActionHandlers,
        handleHistory: openHistoryModal,
    };

    // Tablo sütunları için stil sınıflarını hazırlıyoruz
    const columnClassNames = {
        cellContent: styles.formDataListScreen__cellContent,
        buttonInfo: `${styles.formDataListScreen__actionButton} ${styles.formDataListScreen__actionButton_info}`,
        buttonPrimary: `${styles.formDataListScreen__actionButton} ${styles.formDataListScreen__actionButton_primary}`,
        buttonSecondary: `${styles.formDataListScreen__actionButton} ${styles.formDataListScreen__actionButton_secondary}`,
    };

    // Ana Tablo için Sütunlar (Tüm butonları içerir)
    const submissionColumns = useSubmissionColumns(
        currentForm, user, allActionHandlers, columnClassNames, 'mainList'
    );

    // Geçmiş Modalı için Sütunlar (Sadece 'Görüntüle' butonunu içerir)
    const historyColumns = useSubmissionColumns(
        currentForm, user, allActionHandlers, columnClassNames, 'historyModal'
    );

    useEffect(() => {
        if (formId) {
            fetchForm(formId);
            fetchSubmissions(formId);
        }
    }, [formId, fetchForm, fetchSubmissions]);

    // Yükleme ve hata durumlarını yönetiyoruz
    if (formLoading && !currentForm) return <div>Veriler Yükleniyor...</div>;
    if (formError) return <div className="alert alert-danger">Hata: {formError}</div>;
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

            {/* Görüntüleme Modalı */}
            {selectedSubmission && (
                 <ViewSubmissionModal
                    isOpen={isViewModalOpen}
                    onClose={() => setViewModalOpen(false)}
                    submission={selectedSubmission}
                />
            )}
           
            {/* Düzenleme Modalı */}
            {submissionToEdit && (
                <UpdateSubmissionModal
                    isOpen={isUpdateModalOpen}
                    onClose={() => setUpdateModalOpen(false)}
                    submission={submissionToEdit}
                    formSchema={currentForm}
                    onUpdate={updateSubmission}
                />
            )}

            {/* Geçmiş Modalı (Artık 'historyColumns'u kullanıyor) */}
            <SubmissionHistoryModal
                isOpen={isHistoryModalOpen}
                onClose={closeHistoryModal}
                submission={selectedSubmissionForHistory}
                history={submissionHistory}
                isLoading={historyLoading}
                columns={historyColumns} 
            />
        </div>
    );
};

export default FormDataListScreen;