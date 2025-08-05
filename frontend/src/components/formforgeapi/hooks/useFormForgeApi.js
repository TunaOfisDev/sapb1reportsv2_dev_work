// path: frontend/src/components/formforgeapi/hooks/useFormForgeApi.js
import { useState, useCallback, useMemo } from "react";
import { useNavigate } from "react-router-dom";
import FormForgeApiApi from "../api/FormForgeApiApi";
// Projenizde bir bildirim sistemi (örn: react-toastify) olduğunu varsayıyoruz.
// import { toast } from 'react-toastify';

/**
 * FormForge API Hook (Ana Beyin)
 * --------------------------------------------------------------------
 * Bu hook, formforgeapi modülünün temel veri işlemlerini ve state'ini yönetir.
 * - Form şemalarını (forms) ve gönderimleri (submissions) listeler.
 * - Tek bir form veya gönderim detayını çeker.
 * - CRUD işlemleri için API çağrılarını yapar (create, update, delete).
 * - Sayfa yönlendirmeleri için `useNavigate` kullanır.
 * - UI'da gösterilecek loading ve error durumlarını yönetir.
 * - react-table için `columns` gibi türetilmiş verileri `useMemo` ile oluşturur.
 *
 * NOT: Bu hook "tasarımcı (designer)" mantığı içermez. Sadece veri odaklıdır.
 * Tasarımcı (sürükle-bırak, alan seçimi) mantığı `useFormForgeDesigner` hook'unda olacaktır.
 */
export default function useFormForgeApi() {
  const navigate = useNavigate();

  // --- STATE MANAGEMENT ---
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const [forms, setForms] = useState([]); // Form şemaları listesi
  const [currentForm, setCurrentForm] = useState(null); // Detayı görüntülenen form şeması
  const [submissions, setSubmissions] = useState([]); // Bir forma ait gönderimlerin listesi
  const [departments, setDepartments] = useState([]); // Form oluştururken seçmek için departman listesi

  // --- API İŞLEMLERİ (CALLBACKS) ---

  // Hata yönetimi için yardımcı fonksiyon
  const handleError = (err, message = "Bir hata oluştu.") => {
    const errorMessage = err.response?.data?.detail || message;
    setError(errorMessage);
    // toast.error(errorMessage);
    console.error(err);
  };

  /** Form Şemaları (Schemas) */
  const fetchForms = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await FormForgeApiApi.getForms();
      // DOĞRU: API'den gelen nesnenin içindeki 'results' dizisini alıyoruz.
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
      return response.data; // Bileşenin anlık olarak veriye ulaşması için
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
      // toast.success("Form başarıyla oluşturuldu!");
      navigate(`/formforgeapi/builder/${response.data.id}`); // Oluşturulan formun tasarım ekranına git
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
      // toast.success("Form silindi.");
    } catch (err) {
      handleError(err, "Form silinirken bir hata oluştu.");
    } finally {
      setLoading(false);
    }
  }, []);
  
  /** Form Gönderimleri (Submissions) */
  const fetchSubmissions = useCallback(async (formId) => {
    setLoading(true);
    setError(null);
    try {
        const response = await FormForgeApiApi.getFormSubmissions({ form: formId });
        setSubmissions(response.data);
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
      // Backend `values` array'i ile birlikte nested create bekliyor.
      const payload = {
        form: formId,
        values: Object.entries(submissionData).map(([fieldId, value]) => ({
          form_field: parseInt(fieldId, 10),
          value: String(value),
        })),
      };
      await FormForgeApiApi.createFormSubmission(payload);
      // toast.success("Form başarıyla gönderildi!");
      // İsteğe bağlı olarak kullanıcıyı bir teşekkür sayfasına yönlendirebilirsiniz.
      navigate(`/formforgeapi/forms`);
    } catch (err) {
      handleError(err, "Form gönderilirken bir hata oluştu.");
    } finally {
      setLoading(false);
    }
  }, [navigate]);

  /** Yardımcı Veriler */
  const fetchDepartments = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
        const response = await FormForgeApiApi.getDepartments();
        // DÜZELTME: Sadece 'results' dizisini alıyoruz.
        // API'den 'results' gelmezse diye de `|| []` ile boş bir dizi garantisi veriyoruz.
        setDepartments(response.data.results || []);
    } catch (err) {
        handleError(err, "Departmanlar getirilirken bir hata oluştu.");
    } finally {
        setLoading(false);
    }
  }, []);


  // --- TÜRETİLMİŞ VERİ (MEMOIZED) ---

  // FormDataListScreen'deki react-table için sütunları dinamik olarak oluşturur.
  const submissionColumns = useMemo(() => {
    if (!currentForm?.fields) return [];

    const dynamicColumns = currentForm.fields
      .sort((a, b) => a.order - b.order) // Alanları sırala
      .map((field) => ({
        Header: field.label,
        accessorKey: `value_${field.id}`, // Her alan için benzersiz bir anahtar
      }));
    
    return [
        {
            Header: "Gönderim Tarihi",
            accessorKey: "created_at",
        },
        ...dynamicColumns
    ];
  }, [currentForm]);

  // `submissionColumns`'a uygun hale getirilmiş, formatlanmış veri.
  const submissionFormattedData = useMemo(() => {
    return submissions.map(submission => {
        const rowData = {
            id: submission.id,
            created_at: new Date(submission.created_at).toLocaleString(),
        };
        submission.values.forEach(val => {
            rowData[`value_${val.form_field}`] = val.value;
        });
        return rowData;
    });
  }, [submissions]);


  // Hook'un dışarıya açtığı arayüz
  return {
    // State
    loading,
    error,
    forms,
    currentForm,
    submissions,
    departments,
    
    // Actions
    fetchForms,
    fetchForm,
    createForm,
    deleteForm,
    fetchSubmissions,
    createSubmission,
    fetchDepartments,

    // Derived Data
    submissionColumns,
    submissionFormattedData,
  };
}