// path: frontend/src/components/formforgeapi/hooks/useFormForgeApi.js

import { useState, useCallback, useContext } from "react";
import { useNavigate } from "react-router-dom";
import FormForgeApiApi from "../api/FormForgeApiApi";
import AuthContext  from "../../../auth/AuthContext";

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
  
  // View Modal State
  const [selectedSubmission, setSelectedSubmission] = useState(null);
  const [isViewModalOpen, setViewModalOpen] = useState(false);
  
  // Update Modal State
  const [submissionToEdit, setSubmissionToEdit] = useState(null);
  const [isUpdateModalOpen, setUpdateModalOpen] = useState(false);

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
      const response = await FormForgeApiApi.getFormSubmissions({ form: formId, is_active: true });
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
        values: Object.entries(submissionData).map(([key, value]) => ({
          form_field: parseInt(key.replace('field_', ''), 10),
          value: value, 
        })),
      };
      await FormForgeApiApi.createFormSubmission(payload);
      fetchSubmissions(formId); // Listeyi anında tazele
    } catch (err) {
      handleError(err, "Form gönderilirken bir hata oluştu.");
    } finally {
      setLoading(false);
    }
  }, [fetchSubmissions]);
  
  const updateSubmission = useCallback(async (submissionId, formId, submissionData) => {
    setLoading(true);
    setError(null);
    try {
      const payload = {
        values: Object.entries(submissionData).map(([key, value]) => ({
          form_field: parseInt(key.replace('field_', ''), 10),
          value: value,
        })),
      };
      await FormForgeApiApi.updateFormSubmission(submissionId, payload);
      fetchSubmissions(formId); // Listeyi anında tazele
    } catch (err) {
      handleError(err, "Form güncellenirken bir hata oluştu.");
    } finally {
      setLoading(false);
    }
  }, [fetchSubmissions]);

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
    setSubmissionToEdit(submission);
    setUpdateModalOpen(true);
  }, []);

  // --- HOOK'UN DIŞARIYA AÇTIĞI ARAYÜZ ---
  return {
    loading,
    error,
    user,
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
    updateSubmission,
    fetchDepartments,
    // View Modal
    isViewModalOpen,
    setViewModalOpen,
    selectedSubmission,
    // Update Modal
    isUpdateModalOpen,
    setUpdateModalOpen,
    submissionToEdit,
    // Eylemler
    actionHandlers: {
      // DÜZELTME: İsimleri 'useSubmissionColumns' hook'unun beklediğiyle eşleştiriyoruz.
      handleView: handleViewClick,
      handleEdit: handleEditClick
    }
  };
}