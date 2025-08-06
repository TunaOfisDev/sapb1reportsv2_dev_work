// path: frontend/src/components/formforgeapi/hooks/useFormForgeApi.js
import { useState, useCallback, useMemo } from "react";
import { useNavigate } from "react-router-dom";
import FormForgeApiApi from "../api/FormForgeApiApi";

export default function useFormForgeApi() {
  const navigate = useNavigate();

  // --- STATE MANAGEMENT ---
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [forms, setForms] = useState([]);
  const [archivedForms, setArchivedForms] = useState([]); // YENİ: Arşivlenmiş formlar için state
  const [currentForm, setCurrentForm] = useState(null);
  const [submissions, setSubmissions] = useState([]);
  const [departments, setDepartments] = useState([]);

  // --- API İŞLEMLERİ (CALLBACKS) ---
  const handleError = (err, message = "Bir hata oluştu.") => {
    const errorMessage = err.response?.data?.detail || message;
    setError(errorMessage);
    console.error(err);
  };

  // GÜNCELLENDİ: Hem aktif hem de arşivlenmiş formları getirebilir
  const fetchForms = useCallback(async (status = 'PUBLISHED') => {
    setLoading(true);
    setError(null);
    try {
      const response = await FormForgeApiApi.getForms({ status });
      if (status === 'PUBLISHED') {
        setForms(response.data.results || []);
      } else if (status === 'ARCHIVED') {
        setArchivedForms(response.data.results || []);
      }
    } catch (err) {
      handleError(err, "Formlar getirilirken bir hata oluştu.");
    } finally {
      setLoading(false);
    }
  }, []);

  const fetchForm = useCallback(async (id) => {
    setLoading(true);
    setError(null);
    setCurrentForm(null);
    try {
      const response = await FormForgeApiApi.getForm(id);
      setCurrentForm(response.data);
      return response.data;
    } catch (err) {
      handleError(err, "Form detayı getirilirken bir hata oluştu.");
    } finally {
      setLoading(false);
    }
  }, []);

  const createForm = useCallback(async (formData) => {
    setLoading(true);
    setError(null);
    try {
      const response = await FormForgeApiApi.createForm(formData);
      navigate(`/formforgeapi/builder/${response.data.id}`);
    } catch (err) {
      handleError(err, "Form oluşturulurken bir hata oluştu.");
    } finally {
      setLoading(false);
    }
  }, [navigate]);

  // GÜNCELLENDİ: Hem aktif hem de arşiv listesini tazeleyecek
  const archiveForm = useCallback(async (id) => {
    setLoading(true);
    setError(null);
    try {
      await FormForgeApiApi.archiveForm(id);
      // Aktif formlar listesinden kaldır
      setForms((prevForms) => prevForms.filter((form) => form.id !== id));
      // Arşiv listesini de tazeleyelim ki hemen görünsün
      fetchForms('ARCHIVED'); 
    } catch (err) {
      handleError(err, "Form arşivlenirken bir hata oluştu.");
    } finally {
      setLoading(false);
    }
  }, [fetchForms]); // fetchForms dependency olarak eklendi

  // GÜNCELLENDİ: Hem arşiv hem de aktif listesini tazeleyecek
  const unarchiveForm = useCallback(async (id) => {
    setLoading(true);
    setError(null);
    try {
      await FormForgeApiApi.unarchiveForm(id);
      // Arşivlenmiş formlar listesinden kaldır
      setArchivedForms((prevForms) => prevForms.filter((form) => form.id !== id));
      // Aktif formlar listesini tazeleyelim ki form oraya geri dönsün
      fetchForms('PUBLISHED');
    } catch (err) {
      handleError(err, "Form arşivden çıkarılırken bir hata oluştu.");
    } finally {
      setLoading(false);
    }
  }, [fetchForms]); // fetchForms dependency olarak eklendi


  // YENİ: Form versiyonu oluşturma fonksiyonu
  const createNewVersion = useCallback(async (id) => {
    setLoading(true);
    setError(null);
    try {
      const response = await FormForgeApiApi.createFormVersion(id);
      const newFormId = response.data.id;
      navigate(`/formforgeapi/builder/${newFormId}`);
      return newFormId;
    } catch (err) {
      handleError(err, "Yeni form versiyonu oluşturulurken hata oluştu.");
    } finally {
      setLoading(false);
    }
  }, [navigate]);

  const fetchSubmissions = useCallback(async (formId) => {
    setLoading(true);
    setError(null);
    try {
      const response = await FormForgeApiApi.getFormSubmissions({ form: formId });
      setSubmissions(response.data.results || []);
    } catch (err) {
      handleError(err, "Form verileri getirilirken bir hata oluştu.");
    } finally {
      setLoading(false);
    }
  }, []);

  const createSubmission = useCallback(async (formId, submissionData) => {
    setLoading(true);
    setError(null);
    try {
      const payload = {
        form: formId,
        values: Object.entries(submissionData).map(([fieldId, value]) => ({
          form_field: parseInt(fieldId, 10),
          value: String(value),
        })),
      };
      await FormForgeApiApi.createFormSubmission(payload);
      navigate(`/formforgeapi`);
    } catch (err) {
      handleError(err, "Form gönderilirken bir hata oluştu.");
    } finally {
      setLoading(false);
    }
  }, [navigate]);

  const fetchDepartments = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await FormForgeApiApi.getDepartments();
      setDepartments(response.data.results || []);
    } catch (err) {
      handleError(err, "Departmanlar getirilirken bir hata oluştu.");
    } finally {
      setLoading(false);
    }
  }, []);

  // --- TÜRETİLMİŞ VERİ (MEMOIZED) ---
  const submissionColumns = useMemo(() => {
    if (!currentForm?.fields) return [];
    const dynamicColumns = currentForm.fields
      .sort((a, b) => a.order - b.order)
      .map((field) => ({ Header: field.label, accessor: `value_${field.id}` }));
    return [ { Header: "Gönderim Tarihi", accessor: "created_at", Cell: ({ value }) => new Date(value).toLocaleString() }, ...dynamicColumns ];
  }, [currentForm]);

  const submissionFormattedData = useMemo(() => {
    if (!submissions) return [];
    return submissions.map(submission => {
        const rowData = { id: submission.id, created_at: submission.created_at };
        submission.values.forEach(val => {
            rowData[`value_${val.form_field}`] = val.value;
        });
        return rowData;
    });
  }, [submissions]);

  // Hook'un dışarıya açtığı arayüz
  return {
    loading,
    error,
    forms,
    archivedForms, // YENİ
    currentForm,
    submissions,
    departments,
    fetchForms,
    fetchForm,
    createForm,
    archiveForm, // GÜNCELLENDİ
    unarchiveForm, // YENİ
    createNewVersion, // YENİ
    deleteForm: archiveForm, // Eski isimlendirmeyi de destekler
    fetchSubmissions,
    createSubmission,
    fetchDepartments,
    submissionColumns,
    submissionFormattedData,
  };
}