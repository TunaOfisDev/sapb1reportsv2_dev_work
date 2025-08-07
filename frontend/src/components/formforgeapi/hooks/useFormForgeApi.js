// path: frontend/src/components/formforgeapi/hooks/useFormForgeApi.js

import { useState, useCallback, useContext } from "react";
import { useNavigate } from "react-router-dom";
import FormForgeApiApi from "../api/FormForgeApiApi";
import AuthContext from "../../../auth/AuthContext";

export default function useFormForgeApi() {
  const navigate = useNavigate();
  const { user } = useContext(AuthContext);

  // --- STATE MANAGEMENT --- (DEĞİŞİKLİK YOK)
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

  // ... (fetchForms, fetchForm, createForm, archiveForm, unarchiveForm, createNewVersion, fetchSubmissions
  //      fonksiyonlarında bir değişiklik yok, aynı kalacaklar) ...
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
        values: Object.entries(submissionData).map(([key, value]) => ({
          form_field: parseInt(key.replace('field_', ''), 10),
          value: value, 
        })),
      };
      await FormForgeApiApi.createFormSubmission(payload);
      // Başarılı gönderimden sonra ana listeye değil, formun veri listesine yönlendirelim.
      navigate(`/formforgeapi/data/${formId}`);
    } catch (err) {
      handleError(err, "Form gönderilirken bir hata oluştu.");
    } finally {
      setLoading(false);
    }
  }, [navigate]);
  
  // --- YENİ FONKSİYON: GÖNDERİM GÜNCELLEME ---
  const updateSubmission = useCallback(async (submissionId, formId, submissionData) => {
    setLoading(true);
    setError(null);
    try {
      // Payload, createSubmission ile aynı formatta olmalı
      const payload = {
        values: Object.entries(submissionData).map(([key, value]) => ({
          form_field: parseInt(key.replace('field_', ''), 10),
          value: value,
        })),
      };
      await FormForgeApiApi.updateFormSubmission(submissionId, payload);
      // Başarılı güncellemeden sonra ilgili formun veri listesine geri dön
      navigate(`/formforgeapi/data/${formId}`);
    } catch (err) {
      handleError(err, "Form güncellenirken bir hata oluştu.");
    } finally {
      setLoading(false);
    }
  }, [navigate]);


  const fetchDepartments = useCallback(async () => {
    // ... (bu fonksiyon aynı kalacak) ...
  }, []);

  // --- GÜNCELLENEN EYLEM YÖNETİCİLERİ (ACTION HANDLERS) ---
  const handleViewClick = useCallback((submission) => {
    setSelectedSubmission(submission);
    setViewModalOpen(true);
  }, []);

  const handleEditClick = useCallback((submission) => {
    // Artık alert göstermek yerine, kullanıcıyı düzenleme ekranına yönlendiriyoruz.
    // `state` ile submission verisini de göndererek, yeni sayfada tekrar API isteği yapmaktan kurtuluyoruz.
    navigate(`/formforgeapi/edit/${submission.id}`, { state: { submission } });
  }, [navigate]);


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
    updateSubmission, // <-- Yeni fonksiyonu dışa aktar
    fetchDepartments,
    isViewModalOpen,
    setViewModalOpen,
    selectedSubmission,
    actionHandlers: {
      handleViewClick,
      handleEditClick
    }
  };
}