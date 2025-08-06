// path: frontend/src/components/formforgeapi/hooks/useFormForgeApi.js

import { useState, useCallback, useMemo, useContext } from "react";
import { useNavigate } from "react-router-dom";
import FormForgeApiApi from "../api/FormForgeApiApi";
import AuthContext from "../../../auth/AuthContext";

export default function useFormForgeApi() {
  const navigate = useNavigate();
  
  const { user } = useContext(AuthContext);

  // --- STATE MANAGEMENT ---
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [forms, setForms] = useState([]);
  const [archivedForms, setArchivedForms] = useState([]);
  const [currentForm, setCurrentForm] = useState(null);
  const [submissions, setSubmissions] = useState([]);
  const [departments, setDepartments] = useState([]);

  const [selectedSubmission, setSelectedSubmission] = useState(null);
  const [isViewModalOpen, setViewModalOpen] = useState(false);

  // --- API İŞLEMLERİ (CALLBACKS) ---
  const handleError = (err, message = "Bir hata oluştu.") => {
    const errorMessage = err.response?.data?.detail || err.message || message;
    setError(errorMessage);
    console.error("Hook Hatası:", err);
  };

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

  const archiveForm = useCallback(async (id) => {
    setLoading(true);
    setError(null);
    try {
      await FormForgeApiApi.archiveForm(id);
      setForms((prevForms) => prevForms.filter((form) => form.id !== id));
      fetchForms('ARCHIVED'); 
    } catch (err) {
      handleError(err, "Form arşivlenirken bir hata oluştu.");
    } finally {
      setLoading(false);
    }
  }, [fetchForms]);

  const unarchiveForm = useCallback(async (id) => {
    setLoading(true);
    setError(null);
    try {
      await FormForgeApiApi.unarchiveForm(id);
      setArchivedForms((prevForms) => prevForms.filter((form) => form.id !== id));
      fetchForms('PUBLISHED');
    } catch (err) {
      handleError(err, "Form arşivden çıkarılırken bir hata oluştu.");
    } finally {
      setLoading(false);
    }
  }, [fetchForms]);

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

  // --- EYLEM YÖNETİCİLERİ (ACTION HANDLERS) ---
  const handleViewClick = useCallback((submission) => {
    setSelectedSubmission(submission);
    setViewModalOpen(true);
  }, []);

  const handleEditClick = useCallback((submission) => {
    console.log("Düzenlenecek Veri:", submission);
    alert(`ID: ${submission.id} olan veri düzenlenecek.`);
  }, []);

  // --- TÜRETİLMİŞ VERİ (MEMOIZED) ---
  const submissionColumns = useMemo(() => {
    if (!currentForm?.fields) return [];

    const dynamicColumns = currentForm.fields
      .sort((a, b) => a.order - b.order)
      .map((field) => ({
        Header: field.label,
        accessor: (row) => {
          const valueObj = row.values.find(v => v.form_field === field.id);
          return valueObj ? valueObj.value : "—";
        },
        id: `field_${field.id}`,
      }));

    const staticColumns = [
      {
        Header: "Gönderen",
        // DÜZELTME: CustomUser modelinizde 'username' olmadığı için 'email' kullanılıyor.
        accessor: (row) => row.created_by?.email || "Bilinmiyor",
        id: 'created_by'
      },
      {
        Header: "Gönderim Tarihi",
        accessor: 'created_at',
        Cell: ({ value }) => new Date(value).toLocaleString(),
        id: 'created_at'
      },
      {
        Header: "Eylemler",
        id: "actions",
        Cell: ({ row }) => (
          <div className="d-flex gap-2">
            <button
              className="btn btn-sm btn-outline-info"
              onClick={() => handleViewClick(row.original)}
            >
              Görüntüle
            </button>
            {user && user.id === row.original.created_by?.id && (
              <button
                className="btn btn-sm btn-outline-primary"
                onClick={() => handleEditClick(row.original)}
              >
                Düzenle
              </button>
            )}
          </div>
        ),
      },
    ];

    return [...dynamicColumns, ...staticColumns];
  }, [currentForm, user, handleViewClick, handleEditClick]);

  // Hook'un dışarıya açtığı arayüz
  return {
    loading,
    error,
    forms,
    archivedForms,
    currentForm,
    submissions,
    departments,
    fetchForms,
    fetchForm,
    createForm,
    archiveForm,
    unarchiveForm,
    createNewVersion,
    deleteForm: archiveForm,
    fetchSubmissions,
    createSubmission,
    fetchDepartments,
    submissionColumns,
    isViewModalOpen,
    setViewModalOpen,
    selectedSubmission
  };
}