// frontend/src/components/NewCustomerForm/containers/NewCustomerFormDashboard.js
import { useEffect, useState, useMemo, useCallback } from 'react';
import useNCFDashboard from '../hooks/useNCFDashboard';
import useNCFResendMail from '../hooks/useNCFResendMail';
import customerFormToasts from '../utils/toast';
import Pagination from '../utils/pagination';
import '../css/NewCustomerFormDashboard.css';
import FormShowModal from '../utils/formShowModal';
import { updateUserNewCustomerForm } from '../../../api/newcustomerform';

const NewCustomerFormDashboard = () => {
  /* ------------------------------------------------------------------ */
  const { forms, loading, error, refresh } = useNCFDashboard();
  const { isResending, resendMail } = useNCFResendMail(refresh);

  const [pageIndex, setPageIndex] = useState(0);
  const [pageSize,  setPageSize]  = useState(20);

  const [isModalOpen, setIsModalOpen]  = useState(false);
  const [selectedForm, setSelectedForm]= useState(null);

  /* ---------- DEBUG LOG’LARI GERİ KOYDUK ---------- */
  useEffect(() => {
    console.log('[Dashboard] forms/loading/error değişti →', {
      count  : forms?.length,
      loading,
      error,
      forms,
    });
  }, [forms, loading, error]);

  useEffect(() => {
    console.log('[Dashboard] sadece forms değişti →', { count: forms?.length });
  }, [forms]);

  /* ------------------------------------------------------------------ */
  /* Sayfalama hesapları                                                */
  /* ------------------------------------------------------------------ */
  const pageCount = useMemo(
    () => Math.ceil(forms.length / pageSize) || 1,
    [forms.length, pageSize],
  );
  const currentPageData = useMemo(
    () => forms.slice(pageIndex * pageSize, (pageIndex + 1) * pageSize),
    [forms, pageIndex, pageSize],
  );
  const gotoPage     = useCallback(i => setPageIndex(Math.min(Math.max(i,0), pageCount-1)), [pageCount]);
  const nextPage     = () => gotoPage(pageIndex + 1);
  const previousPage = () => gotoPage(pageIndex - 1);

  /* ------------------------------------------------------------------ */
  /* Diğer aksiyonlar                                                   */
  /* ------------------------------------------------------------------ */
  const openEditModal  = f => { setSelectedForm(f); setIsModalOpen(true); };
  const closeModal     = () => { setIsModalOpen(false); setSelectedForm(null); };

  const handleFormSubmit = async data => {
    await updateUserNewCustomerForm(selectedForm.id, data)
      .then(() => {
        customerFormToasts.success('Form başarıyla güncellendi');
        closeModal();
        refresh();
      })
      .catch(err => {
        customerFormToasts.error('Form güncellenirken hata oluştu');
        throw err;
      });
  };

  /* ------------------------------------------------------------------ */
  if (loading)   return <div className="new-customer-form-dashboard__message">Yükleniyor…</div>;
  if (error)     return <div className="new-customer-form-dashboard__message">Hata: {error.message}</div>;
  if (!forms.length) return <div className="new-customer-form-dashboard__message">Hiç form bulunamadı.</div>;

  /* ------------------------------------------------------------------ */
  return (
    <>
      <div className="new-customer-form-dashboard">
  <div className="new-customer-form-dashboard__top-bar">
    <div className="new-customer-form-dashboard__pagination-wrapper">
      <Pagination
        canNextPage={pageIndex < pageCount - 1}
        canPreviousPage={pageIndex > 0}
        pageCount={pageCount}
        pageIndex={pageIndex}
        pageSize={pageSize}
        gotoPage={gotoPage}
        nextPage={nextPage}
        previousPage={previousPage}
        setPageSize={size => {
          setPageIndex(0);
          setPageSize(size);
        }}
      />
    </div>
    <h2 className="new-customer-form-dashboard__title">Oluşturduğunuz Formlar</h2>
  </div>

  <table className="new-customer-form-dashboard__table">
    <thead className="new-customer-form-dashboard__table-head">
      <tr className="new-customer-form-dashboard__table-row">
        <th className="new-customer-form-dashboard__table-header">ID</th>
        <th className="new-customer-form-dashboard__table-header">Firma Ünvanı</th>
        <th className="new-customer-form-dashboard__table-header">Mail Durumu</th>
        <th className="new-customer-form-dashboard__table-header">Mail Alıcısı</th>
        <th className="new-customer-form-dashboard__table-header">Son Gönderim</th>
        <th className="new-customer-form-dashboard__table-header">İşlemler</th>
      </tr>
    </thead>
    <tbody>
      {currentPageData.map((form) => {
        const log = form.mail_status;
        return (
          <tr key={form.id} className="new-customer-form-dashboard__table-row">
            <td className="new-customer-form-dashboard__table-cell">{form.id}</td>
            <td className="new-customer-form-dashboard__table-cell">{form.firma_unvani}</td>
            <td className="new-customer-form-dashboard__table-cell">
              {log?.status_display || 'Gönderilmedi'}
            </td>
            <td className="new-customer-form-dashboard__table-cell">
              {log?.recipients_display || '-'}
            </td>
            <td className="new-customer-form-dashboard__table-cell">
              {log?.created_at
                ? new Date(log.created_at).toLocaleString('tr-TR')
                : '-'}
            </td>
            <td className="new-customer-form-dashboard__table-cell">
              <div className="new-customer-form-dashboard__button-group">
                <button
                  className="new-customer-form-dashboard__button new-customer-form-dashboard__button--edit"
                  onClick={() => openEditModal(form)}
                >
                  Düzenle
                </button>
                <button
                  className="new-customer-form-dashboard__button new-customer-form-dashboard__button--mail"
                  onClick={() => resendMail(form.id)}
                  disabled={isResending || log?.status === 'SENDING'}
                >
                  {isResending ? 'Gönderiliyor…' : 'Mail Gönder'}
                </button>
              </div>
            </td>
          </tr>
        );
      })}
    </tbody>
  </table>
</div>


      <FormShowModal
        isOpen   ={isModalOpen}
        onClose  ={closeModal}
        formData ={selectedForm}
        onSubmit ={handleFormSubmit}
      />
    </>
  );
};

export default NewCustomerFormDashboard;
