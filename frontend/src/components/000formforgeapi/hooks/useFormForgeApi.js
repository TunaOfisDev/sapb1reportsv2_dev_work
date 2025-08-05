// path: frontend/src/components/formforgeapi/hooks/useFormForgeApi.js
import { useState, useEffect, useCallback, useMemo } from "react";
import { useForm } from "react-hook-form";
import { yupResolver } from "@hookform/resolvers/yup";
import * as yup from "yup";
import { useTable } from "react-table";
import FormForgeApiApi from "../api/FormForgeApiApi";
import { useNavigate, useParams } from "react-router-dom";
import {
  addEmptyOption,
  updateOptionLabel,
  deleteOption,
} from "../utils/optionUtils";

const useFormForgeApi = () => {
  const [forms, setForms] = useState([]);
  const [currentForm, setCurrentForm] = useState(null);
  const [submissions, setSubmissions] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isEditing, setIsEditing] = useState(false);
  const [departments, setDepartments] = useState([]);
  const [selectedDepartment, setSelectedDepartment] = useState("");
  const { id } = useParams();
  const navigate = useNavigate();

  /* -------- HELPER FUNCTION: LEGACY VERİYİ DÖNÜŞTÜRME -------- */
  // 'select' legacy verisini yeni standarda ('singleselect') dönüştürür.
  const normalizeFieldType = (ft) =>
    ft === "select" ? "singleselect" : ft;

  /* -------- OPTION HELPERS -------- */
  const handleAddOption = (fieldId) => {
    setCurrentForm((prev) => ({
      ...prev,
      fields: prev.fields.map((f) =>
        f.id === fieldId
          ? { ...f, options: addEmptyOption(f.options) }
          : f
      ),
    }));
  };

  const handleOptionLabelChange = (fieldId, optionId, newLabel) => {
    setCurrentForm((prev) => ({
      ...prev,
      fields: prev.fields.map((f) =>
        f.id === fieldId
          ? {
              ...f,
              options: updateOptionLabel(f.options, optionId, newLabel),
            }
          : f
      ),
    }));
  };

  const handleDeleteOption = (fieldId, optionId) => {
    setCurrentForm((prev) => ({
      ...prev,
      fields: prev.fields.map((f) =>
        f.id === fieldId
          ? { ...f, options: deleteOption(f.options, optionId) }
          : f
      ),
    }));
  };

  const formSchema = yup.object().shape({
    title: yup.string().required("Title is required"),
    description: yup.string(),
  });

  const {
    control,
    handleSubmit,
    reset,
    formState: { errors },
    setValue,
    register,
  } = useForm({
    resolver: yupResolver(formSchema),
  });

  const fetchForms = useCallback(async () => {
    setIsLoading(true);
    try {
      const response = await FormForgeApiApi.getForms();
      setForms(response.data.results || response.data || []);
    } catch (error) {
      console.error("Error fetching forms:", error);
    } finally {
      setIsLoading(false);
    }
  }, []);

  const fetchDepartments = useCallback(async () => {
    try {
      const response = await FormForgeApiApi.getDepartments();
      setDepartments(response.data.results || response.data || []);
    } catch (error) {
      console.error("Error fetching departments:", error);
    }
  }, []);

  const fetchForm = useCallback(async (formId) => {
    setIsLoading(true);
    try {
      const response = await FormForgeApiApi.getForm(formId);
      // Eski "select" değerini tek yerde dönüştür
      const cleanedFields = response.data.fields.map((f) => ({
        ...f,
        field_type: normalizeFieldType(f.field_type),
      }));

      setCurrentForm({ ...response.data, fields: cleanedFields });
      setSelectedDepartment(response.data.department);
      reset({
        title: response.data.title,
        description: response.data.description,
      });
      setIsEditing(true);
    } catch (error) {
      console.error("Error fetching form:", error);
    } finally {
      setIsLoading(false);
    }
  }, [reset]);

  const fetchSubmissions = useCallback(async (formId) => {
    setIsLoading(true);
    try {
      const response = await FormForgeApiApi.getFormSubmissions({ form: formId });

      // ⬇️ DİZİ GARANTİSİ
      setSubmissions(response.data.results || response.data || []);
    } catch (error) {
      console.error("Error fetching submissions:", error);
    } finally {
      setIsLoading(false);
    }
  }, []);



  useEffect(() => {
    fetchForms();
    fetchDepartments();
  }, [fetchForms, fetchDepartments]);

  useEffect(() => {
    if (id) {
      fetchForm(id);
      fetchSubmissions(id);
    } else {
      setCurrentForm({ title: "", description: "", fields: [] });
      setIsEditing(false);
      setSelectedDepartment("");
    }
  }, [id, fetchForm, fetchSubmissions]);

  const handleFieldChange = (event, fieldId = null) => {
    const { name, value } = event.target;
    setCurrentForm((prevForm) => {
      if (fieldId) {
        return {
          ...prevForm,
          fields: prevForm.fields.map((field) =>
            field.id === fieldId ? { ...field, [name]: value } : field
          ),
        };
      }
      return {
        ...prevForm,
        [name]: value,
      };
    });
  };

  const handleAddFormField = () => {
    setCurrentForm((prevForm) => ({
      ...prevForm,
      fields: [
        ...prevForm.fields,
        {
          id: `temp_${Date.now()}`,
          label: "",
          field_type: "text",
          is_required: false,
          is_master: false,
          order: prevForm.fields.length,
          options: [],
        },
      ],
    }));
  };

  // Yeni, doğru çalışan handleDeleteFormField fonksiyonu
  const handleDeleteFormField = async (fieldId) => {
    try {
      // Eğer ID "temp_" ile başlamıyorsa, backend'den kalıcı olarak sil
      if (fieldId && !String(fieldId).startsWith("temp_")) {
        await FormForgeApiApi.deleteFormField(fieldId);
      }
      
      // Frontend state'inden her durumda kaldır
      setCurrentForm((prevForm) => ({
        ...prevForm,
        fields: prevForm.fields.filter((field) => field.id !== fieldId),
      }));
    } catch (error) {
      console.error("Error deleting form field:", error);
      // Hata durumunda, kullanıcıya bilgilendirme yapmak veya eski state'e dönmek gerekebilir
      alert("Form alanı silinirken bir hata oluştu. Lütfen tekrar deneyin.");
    }
  };

  const handleOnDragEnd = (result) => {
    if (!result.destination) return;
    const reorderedFields = Array.from(currentForm.fields);
    const [reorderedItem] = reorderedFields.splice(result.source.index, 1);
    reorderedFields.splice(result.destination.index, 0, reorderedItem);

    const updatedOrder = reorderedFields.map((field, index) => ({
      id: field.id,
      order: index,
    }));

    FormForgeApiApi.updateFormFieldOrder(updatedOrder)
      .then(() => {
        setCurrentForm((prevForm) => ({
          ...prevForm,
          fields: reorderedFields,
        }));
      })
      .catch((error) => {
        console.error("Error updating field order:", error);
      });
  };

  const handleSaveForm = async () => {
    setIsSubmitting(true);
    try {
      const formResponse = isEditing
        ? await FormForgeApiApi.updateForm(id, {
            title: currentForm.title,
            description: currentForm.description,
            ...(selectedDepartment && { department: selectedDepartment }),
          })
        : await FormForgeApiApi.createForm({
            title: currentForm.title,
            description: currentForm.description,
            ...(selectedDepartment && { department: selectedDepartment }),
          });

      const formId = formResponse.data.id;
      
      const saveFieldPromises = (currentForm.fields || []).map((field) => {
        const fieldData = {
          form: formId,
          label: field.label,
          field_type: normalizeFieldType(field.field_type), // Eski "select" değerini dönüştür
          is_required: field.is_required,
          order: field.order,

          /* 🔽 EKSTRA: boş label’lı option’ları atla */
          options:
            (field.options || [])
              .filter((o) => o.label && o.label.trim())
              .map((o, idx) => ({
                label: o.label.trim(),
                order: idx,
              })),
        };

        if (field.id && !String(field.id).startsWith("temp_")) {
          return FormForgeApiApi.updateFormField(field.id, fieldData);
        } else {
          return FormForgeApiApi.createFormField(fieldData);
        }
      });
      
      await Promise.all(saveFieldPromises);
      navigate(`/formforgeapi/builder/${formId}`);
    } catch (error) {
      console.error("Error saving form:", error);
    } finally {
      setIsSubmitting(false);
    }
  };

  const onSubmit = async (formData) => {
    setIsSubmitting(true);
    try {
      const submissionValues = (currentForm.fields || [])
        .map((field) => {
          if (field.id && !String(field.id).startsWith("temp_")) {
            const value = formData[field.label];
            if (Array.isArray(value)) value.join(",");
            if (value !== null && value !== undefined && value !== '') {
              return {
                // Burada submission alanına form ID'sini atıyoruz
                submission: currentForm.id,
                form_field: field.id,
                value: value,
              };
            }
          }
          return null;
        })
        .filter(Boolean);

      // Zorunlu alan kontrolü
      if (submissionValues.length === 0) {
        console.error("Hiçbir form değeri gönderilmedi. Lütfen alanları doldurun.");
        setIsSubmitting(false);
        return;
      }
      
      const submissionData = {
        form: currentForm.id,
        values: submissionValues,
      };

      const submissionResponse = await FormForgeApiApi.createFormSubmission(submissionData);
      
      console.log("Form submitted successfully:", submissionResponse.data);
      reset();
      
      fetchSubmissions(currentForm.id);
      navigate('/formforgeapi');
    } catch (error) {
      console.error("Error submitting form:", error);
      const apiError = error.response?.data || error.message;
      console.error("API Hatası Detayları:", apiError);
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleDeleteForm = async (formId) => {
    try {
      await FormForgeApiApi.deleteForm(formId);
      setForms((prevForms) =>
        prevForms.filter((form) => form.id !== formId)
      );
    } catch (error) {
      console.error("Error deleting form:", error);
    }
  };

  const handleEditForm = (formId) => {
    navigate(`/formforgeapi/builder/${formId}`);
  };

  const columns = useMemo(() => {
    if (!currentForm) return [];

    return currentForm.fields.map((field) => ({
      Header: field.label,

      /* Fonksiyonel accessor: ilgili form_field id’sini bulup value döndürür */
      accessor: (row) => {
        const found = Array.isArray(row.values)
          ? row.values.find((v) => v.form_field === field.id)
          : null;
        return found ? found.value : "";
      },
    }));
  }, [currentForm]);


  return {
    forms,
    currentForm,
    isLoading,
    isSubmitting,
    submissions,
    columns,
    departments,
    selectedDepartment,
    setSelectedDepartment,
    control,
    handleSubmit,
    errors,
    register,
    handleFieldChange,
    handleAddFormField,
    handleDeleteFormField,
    handleOnDragEnd,
    handleSaveForm,
    onSubmit,
    handleDeleteForm,
    handleEditForm,
    handleAddOption,
    handleOptionLabelChange,
    handleDeleteOption,
  };
};

export default useFormForgeApi;