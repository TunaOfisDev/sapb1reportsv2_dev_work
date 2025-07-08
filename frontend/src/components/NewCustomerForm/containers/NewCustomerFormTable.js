// frontend/src/components/NewCustomerForm/containers/NewCustomerFormTable.js
import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { getUserNewCustomerForms } from '../../../api/newcustomerform';
import { getAllMailLogs, resendFormMail } from '../../../api/mailservice';
import customerFormToasts from '../utils/toast';
import '../css/NewCustomerFormTable.css';

const NewCustomerFormTable = () => {
  const [forms, setForms] = useState([]);
  const [mailLogs, setMailLogs] = useState({});
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    const fetchData = async () => {
      try {
        // Forms verilerini çek
        const formsResponse = await getUserNewCustomerForms();
        const formsList = formsResponse.results || formsResponse;
        console.log('1. Formlar yüklendi:', formsList);
        
        // Mail loglarını çek
        const mailLogsResponse = await getAllMailLogs();
        console.log('2. Mail logları yüklendi:', mailLogsResponse);

        // Mail loglarını form ID'ye göre grupla
        const mailStatusMap = {};
        if (mailLogsResponse?.results) {
          mailLogsResponse.results.forEach(log => {
            const formId = parseInt(log.related_object_id);
            console.log('3. Log işleniyor:', { formId, log });

            if (formId && (!mailStatusMap[formId] || 
                new Date(log.created_at) > new Date(mailStatusMap[formId].created_at))) {
              console.log('4. Form için yeni log kaydı:', { formId, log });
              mailStatusMap[formId] = {
                status: log.status,
                status_display: log.status_display,
                recipients_display: log.recipients_display,
                created_at: log.created_at,
                sent_at: log.sent_at,
                related_object_id: formId
              };
            }
          });
        }

        console.log('5. Oluşturulan Mail Status Map:', mailStatusMap);
        setForms(formsList);
        setMailLogs(mailStatusMap);

      } catch (error) {
        console.error('6. Veri çekilirken hata:', error);
        customerFormToasts.error('Veriler alınırken hata oluştu');
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  const handleEdit = (formId) => {
    navigate(`/newcustomerform/edit/${formId}`);
  };

  const handleResend = async (formId) => {
    try {
      console.log('7. Mail yeniden gönderiliyor:', formId);
      customerFormToasts.mail.sending();
      await resendFormMail(formId);

      // Mail loglarını güncelle
      const logsData = await getAllMailLogs();
      console.log('8. Yeni mail logları:', logsData);
      
      const logsMap = {};
      if (logsData && logsData.results) {
        logsData.results.forEach(log => {
          const logFormId = parseInt(log.related_object_id);
          console.log('9. Log güncelleniyor:', { logFormId, log });
          
          if (log.related_object_type === 'NewCustomerForm' && logFormId) {
            if (!logsMap[logFormId] || 
                new Date(log.created_at) > new Date(logsMap[logFormId].created_at)) {
              logsMap[logFormId] = {
                status: log.status,
                status_display: log.status_display,
                recipients_display: log.recipients_display,
                created_at: log.created_at,
                sent_at: log.sent_at,
                related_object_id: logFormId
              };
            }
          }
        });
      }
      
      console.log('10. Güncellenmiş logs map:', logsMap);
      setMailLogs(logsMap);
      customerFormToasts.mail.success();
    } catch (error) {
      console.error('11. Mail gönderme hatası:', error);
      customerFormToasts.mail.error('Mail yeniden gönderilemedi');
    }
  };

  // Table render edilmeden önce son kontrol
  console.log('12. Render öncesi state:', { forms, mailLogs });

  if (loading) {
    return (
      <div className="new-customer-form-table__loading">
        <div className="new-customer-form-table__loading-spinner"></div>
        Yükleniyor...
      </div>
    );
  }

  if (!forms || forms.length === 0) {
    return (
      <div className="new-customer-form-table new-customer-form-table--no-data">
        Hiç form bulunamadı.
      </div>
    );
  }
  console.log('Render başlıyor - Mevcut state:', { forms, mailLogs });
  return (
    <table className="new-customer-form-table">
      <thead className="new-customer-form-table__thead">
        <tr className="new-customer-form-table__row">
          <th className="new-customer-form-table__header">ID</th>
          <th className="new-customer-form-table__header">Firma Ünvanı</th>
          <th className="new-customer-form-table__header">Mail Durumu</th>
          <th className="new-customer-form-table__header">Mail Alıcısı</th>
          <th className="new-customer-form-table__header">Son Gönderim</th>
          <th className="new-customer-form-table__header">İşlemler</th>
        </tr>
      </thead>
      <tbody>
      {forms.map(form => {
          const formId = parseInt(form.id);
          const mailLog = mailLogs[formId];
          console.log(`Form ${formId} render ediliyor:`, {
            form,
            mailLog,
            hasMailLog: !!mailLog
          });

          return (
            <tr key={formId} className="new-customer-form-table__row">
              <td className="new-customer-form-table__cell">{formId}</td>
              <td className="new-customer-form-table__cell">{form.firma_unvani}</td>
              <td className="new-customer-form-table__cell">
                {mailLog?.status_display || 'Gönderilmedi'}
              </td>
              <td className="new-customer-form-table__cell">
                {mailLog?.recipients_display || '-'}
              </td>
              <td className="new-customer-form-table__cell">
                {mailLog ? new Date(mailLog.created_at).toLocaleString('tr-TR') : '-'}
              </td>
              <td className="new-customer-form-table__cell">
                <div className="new-customer-form-table__button-group">
                  <button
                    onClick={() => handleEdit(formId)}
                    className="new-customer-form-table__button new-customer-form-table__button--edit"
                  >
                    Düzenle
                  </button>
                  <button
                    onClick={() => handleResend(formId)}
                    className="new-customer-form-table__button new-customer-form-table__button--mail"
                    disabled={mailLog?.status === 'SENDING'}
                  >
                    Mail Gönder
                  </button>
                </div>
              </td>
            </tr>
          );
        })}
      </tbody>
    </table>
  );
};

export default NewCustomerFormTable;