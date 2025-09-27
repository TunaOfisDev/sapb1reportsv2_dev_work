// frontend/src/components/NewCustomerForm/hooks/useNCFDashboard.js
import { useState, useEffect, useCallback } from 'react';
import { getUserNewCustomerForms } from '../../../api/newcustomerform';
import { getAllMailLogs } from '../../../api/mailservice';

const useNCFDashboard = () => {
  const [forms, setForms] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchForms = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      // Form ve mail verilerini paralel çek
      const [formsData, mailLogsData] = await Promise.all([
        getUserNewCustomerForms(),
        getAllMailLogs()
      ]);

      // Mail loglarını ID'ye göre grupla
      const mailLogsMap = {};
      if (mailLogsData?.results) {
        mailLogsData.results.forEach(log => {
          if (log.related_object_type === 'NewCustomerForm' && log.related_object_id) {
            const formId = parseInt(log.related_object_id);
            if (
              !mailLogsMap[formId] ||
              new Date(log.created_at) > new Date(mailLogsMap[formId].created_at)
            ) {
              mailLogsMap[formId] = {
                status_display: log.status_display,
                recipients_display: log.recipients_display,
                created_at: log.created_at,
                status: log.status
              };
            }
          }
        });
      }

      // Formlara mail log ekle
      let enrichedForms = formsData.map(form => ({
        ...form,
        mail_status: mailLogsMap[form.id] || null
      }));

      // ID'ye göre büyükten küçüğe sırala (Z → A)
      enrichedForms.sort((a, b) => b.id - a.id);

      setForms(enrichedForms);
    } catch (err) {
      console.error('Dashboard verileri alınırken hata:', err);
      setError(err);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchForms();
  }, [fetchForms]);

  return {
    forms,
    loading,
    error,
    refresh: fetchForms,
  };
};

export default useNCFDashboard;
