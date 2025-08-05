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
  const [currentForm, setCurrentForm] = useState(null);
  const [submissions, setSubmissions] = useState([]);
  const [departments, setDepartments] = useState([]);

  // --- API İŞLEMLERİ (CALLBACKS) ---
  const handleError = (err, message = "Bir hata oluştu.") => {
    const errorMessage = err.response?.data?.detail || message;
    setError(errorMessage);
    console.error(err);
  };

  const fetchForms = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await FormForgeApiApi.getForms();
      setForms(response.data.results || []); 
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

  const deleteForm = useCallback(async (id) => {
    setLoading(true);
    setError(null);
    try {
      await FormForgeApiApi.deleteForm(id);
      setForms((prevForms) => prevForms.filter((form) => form.id !== id));
    } catch (err) {
      handleError(err, "Form silinirken bir hata oluştu.");
    } finally {
      setLoading(false);
    }
  }, []);
  
  const fetchSubmissions = useCallback(async (formId) => {
    setLoading(true);
    setError(null);
    try {
      const response = await FormForgeApiApi.getFormSubmissions({ form: formId });
      // DÜZELTME: Sadece 'results' dizisini alıyoruz.
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
      navigate(`/formforgeapi/forms`);
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

  // GÜNCELLENMİŞ BLOK (v7 UYUMLU)
  const submissionColumns = useMemo(() => {
    if (!currentForm?.fields) return [];

    const dynamicColumns = currentForm.fields
      .sort((a, b) => a.order - b.order)
      .map((field) => ({
        Header: field.label,
        accessor: `value_${field.id}`, // v7 için 'accessor'
      }));
    
    return [
        {
            Header: "Gönderim Tarihi",
            accessor: "created_at", // v7 için 'accessor'
            Cell: ({ value }) => new Date(value).toLocaleString(), // v7 için formatlama
        },
        ...dynamicColumns
    ];
  }, [currentForm]);

  // GÜNCELLENMİŞ BLOK
  const submissionFormattedData = useMemo(() => {
    if (!submissions) return [];
    return submissions.map(submission => {
        const rowData = {
            id: submission.id,
            created_at: submission.created_at, // Orijinal tarihi olduğu gibi bırak
        };
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
    currentForm,
    submissions,
    departments,
    fetchForms,
    fetchForm,
    createForm,
    deleteForm,
    fetchSubmissions,
    createSubmission,
    fetchDepartments,
    submissionColumns,
    submissionFormattedData,
  };
}