// frontend/src/components/NewCustomerForm/hooks/useNewCustomerForm.js
import { useState, useCallback, useEffect } from 'react';
import { createNewCustomerForm, updateUserNewCustomerForm } from '../../../api/newcustomerform';
import { getInitialFormData, validateForm, validateFileSize } from '../utils/formHelpers';
import customerFormToasts from '../utils/toast';
import axiosInstance from '../../../api/axiosconfig';

const useNewCustomerForm = ({ initialData = null, isEdit = false }) => {
  const [formData, setFormData] = useState(initialData || getInitialFormData());
  const [errors, setErrors] = useState({});
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitStatus, setSubmitStatus] = useState({
    success: false,
    mailSent: false,
    message: ''
  });

  // initialData değiştiğinde formData'yı güncelle
  useEffect(() => {
    if (initialData) {
      console.log('Initial form data loaded:', initialData);
      setFormData(initialData);
    }
  }, [initialData]);

  const validateFormCallback = useCallback(() => {
    const newErrors = validateForm(formData);
    setErrors(newErrors);
    if (Object.keys(newErrors).length > 0) {
      customerFormToasts.form.validationError();
      return false;
    }
    return true;
  }, [formData]);

  const handleChange = useCallback((e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  }, []);

  const handleFileChange = useCallback((e) => {
    const { name, files } = e.target;
    if (files?.[0]) {
      const error = validateFileSize(files[0]);
      if (error) {
        setErrors(prev => ({ ...prev, [name]: error }));
        customerFormToasts.fileOperations.uploadError(files[0].name, error);
        return;
      }
      setFormData(prev => ({ ...prev, [name]: files[0] }));
      setErrors(prev => ({ ...prev, [name]: undefined }));
      customerFormToasts.fileOperations.uploadSuccess(files[0].name);
    }
  }, []);

  const handleAddPerson = useCallback(() => {
    setFormData(prev => ({
      ...prev,
      yetkili_kisiler: [...prev.yetkili_kisiler, { ad_soyad: '', telefon: '', email: '' }]
    }));
    customerFormToasts.authorizedPerson.added();
  }, []);

  const handleRemovePerson = useCallback((index) => {
    setFormData(prev => ({
      ...prev,
      yetkili_kisiler: prev.yetkili_kisiler.filter((_, i) => i !== index)
    }));
    setErrors(prev => ({
      ...prev,
      yetkili_kisiler: prev.yetkili_kisiler?.filter((_, i) => i !== index)
    }));
    customerFormToasts.authorizedPerson.removed();
  }, []);

  const handlePersonChange = useCallback((index, field, value) => {
    setFormData(prev => ({
      ...prev,
      yetkili_kisiler: prev.yetkili_kisiler.map((person, i) => 
        i === index ? { ...person, [field]: value } : person
      )
    }));
    setErrors(prev => ({
      ...prev,
      yetkili_kisiler: prev.yetkili_kisiler?.map((error, i) => 
        i === index ? undefined : error
      )
    }));
  }, []);

  const pollMailStatus = (formId, maxAttempts = 5, interval = 2000) => {
    return new Promise((resolve, reject) => {
      let attempts = 0;
      const pollInterval = setInterval(async () => {
        attempts++;
        try {
          const mailResponse = await axiosInstance.get(`mailservice/logs/?related_object_id=${formId}`);
          const logs = mailResponse.data;
          if (logs && logs.length > 0) {
            const latestLog = logs[0];
            if (latestLog.status === 'SENT') {
              clearInterval(pollInterval);
              resolve(true);
              return;
            } else if (latestLog.status === 'FAILED') {
              clearInterval(pollInterval);
              resolve(false);
              return;
            }
          }
          if (attempts >= maxAttempts) {
            clearInterval(pollInterval);
            resolve(false);
          }
        } catch (err) {
          clearInterval(pollInterval);
          reject(err);
        }
      }, interval);
    });
  };

  const handleSubmit = useCallback(async (e) => {
    e.preventDefault();
    
    if (!validateFormCallback()) {
      return;
    }

    customerFormToasts.form.processing();

    const cleanFormData = {
      ...formData,
      yetkili_kisiler: formData.yetkili_kisiler.filter(kisi => 
        kisi.ad_soyad?.trim() && kisi.telefon?.trim() && kisi.email?.trim()
      )
    };

    setIsSubmitting(true);
    
    try {
      let response;
      
      if (isEdit) {
        console.log('Updating form:', cleanFormData);
        response = await updateUserNewCustomerForm(formData.id, cleanFormData);
        customerFormToasts.form.submitSuccess('Form güncellendi');
      } else {
        console.log('Creating new form:', cleanFormData);
        response = await createNewCustomerForm(cleanFormData);
        customerFormToasts.form.submitSuccess('Form kaydedildi. Mail gönderimi kontrol ediliyor...');
      }
      
      const formId = response.data ? response.data.id : response.id;

      if (!isEdit) {
        const mailSent = await pollMailStatus(formId, 5, 2000);
        
        if (mailSent) {
          customerFormToasts.form.submitSuccess('Form kaydedildi ve mail gönderildi');
        } else {
          customerFormToasts.form.submitWarning('Form kaydedildi. Lütfen mail kutunuzu kontrol edin.');
        }
        
        setSubmitStatus({
          success: true,
          mailSent: mailSent,
          message: mailSent ? 'Mail başarıyla gönderildi' : 'Lütfen mail kutunuzu kontrol edin.'
        });

        setFormData(getInitialFormData());
      } else {
        setSubmitStatus({
          success: true,
          message: 'Form başarıyla güncellendi'
        });
      }
      
      setErrors({});
      
    } catch (error) {
      console.error('Form submit error:', error);
      
      setSubmitStatus({
        success: false,
        mailSent: false,
        message: error.message || 'Form işlenirken bir hata oluştu'
      });

      setErrors(prev => ({ 
        ...prev, 
        submit: error.message || 'Form işlenirken bir hata oluştu'
      }));

      customerFormToasts.form.submitError(error.message);
    } finally {
      setIsSubmitting(false);
    }
  }, [formData, validateFormCallback, isEdit]);

  return {
    formData,
    errors,
    isSubmitting,
    submitStatus,
    handleChange,
    handleFileChange,
    handleAddPerson,
    handleRemovePerson,
    handlePersonChange,
    handleSubmit
  };
};

export default useNewCustomerForm;