// frontend/src/components/NewCustomerForm/utils/toast.js
import { toast } from 'react-toastify';

const defaultOptions = {
  position: "top-right",
  autoClose: 5000,
  hideProgressBar: false,
  closeOnClick: true,
  pauseOnHover: true,
  draggable: true,
  progress: undefined,
  theme: "colored"
};

const customerFormToasts = {
  success: (message) => {
    toast.success(message, defaultOptions);
  },

  error: (error) => {
    // API hatalarını işle
    if (error.response) {
      // Backend'den gelen hata mesajlarını işle
      const { data, status } = error.response;
      
      // Validation hataları için (400)
      if (status === 400 && typeof data === 'object') {
        Object.entries(data).forEach(([field, errors]) => {
          if (Array.isArray(errors)) {
            errors.forEach(err => 
              toast.error(`${field}: ${err}`, defaultOptions)
            );
          } else {
            toast.error(`${field}: ${errors}`, defaultOptions);
          }
        });
        return;
      }
      
      // Diğer HTTP hataları için
      const errorMessage = data.detail || data.message || 'Form gönderiminde bir hata oluştu';
      toast.error(errorMessage, defaultOptions);
      return;
    }

    // Network hataları için
    if (error.request) {
      toast.error('Sunucuya bağlanılamadı. Lütfen internet bağlantınızı kontrol edin.', defaultOptions);
      return;
    }

    // Genel hatalar için
    toast.error(error.message || 'Beklenmeyen bir hata oluştu', defaultOptions);
  },

  warn: (message) => {
    toast.warn(message, defaultOptions);
  },

  info: (message) => {
    toast.info(message, defaultOptions);
  },

  // Form-specific toasts
  formValidation: {
    fileSize: (fileName) => {
      toast.error(`${fileName} dosyası 1MB'dan büyük olamaz`, defaultOptions);
    },
    
    requiredField: (fieldName) => {
      toast.error(`${fieldName} alanı zorunludur`, defaultOptions);
    },
    
    invalidEmail: (email) => {
      toast.error(`${email} geçerli bir e-posta adresi değil`, defaultOptions);
    },
    
    invalidPhone: (phone) => {
      toast.error(`${phone} geçerli bir telefon numarası değil`, defaultOptions);
    }
  },

  fileOperations: {
    uploadSuccess: (fileName) => {
      toast.success(`${fileName} başarıyla yüklendi`, defaultOptions);
    },
    
    uploadError: (fileName, error) => {
      toast.error(`${fileName} yüklenirken hata oluştu: ${error}`, defaultOptions);
    },
    
    invalidType: (fileName) => {
      toast.error(`${fileName} desteklenmeyen bir dosya türü`, defaultOptions);
    }
  },

  authorizedPerson: {
    added: () => {
      toast.success('Yetkili kişi başarıyla eklendi', defaultOptions);
    },
    
    removed: () => {
      toast.info('Yetkili kişi kaldırıldı', defaultOptions);
    },
    
    updated: () => {
      toast.success('Yetkili kişi bilgileri güncellendi', defaultOptions);
    }
  },

  form: {
    submitSuccess: () => {
      toast.success('Yeni müşteri formu başarıyla gönderildi', {
        ...defaultOptions,
        autoClose: 3000
      });
    },
    
    submitError: (error) => {
      toast.error(`Form gönderilirken hata oluştu: ${error}`, defaultOptions);
    },
    
    validationError: () => {
      toast.error('Lütfen form alanlarını kontrol ediniz', defaultOptions);
    },
    
    processing: () => {
      toast.info('Form işleniyor, lütfen bekleyin...', {
        ...defaultOptions,
        autoClose: 2000
      });
    },
    
    submitWarning: (message) => {
      toast.warning(message, {
        ...defaultOptions,
        autoClose: 6000
      });
    }
  },

  // Mail gönderimi için yeni toast'lar
  mail: {
    sending: () => {
      toast.info('Mail gönderiliyor...', {
        ...defaultOptions,
        autoClose: 2000
      });
    },

    success: (recipients) => {
      toast.success(`Mail başarıyla gönderildi${recipients ? `: ${recipients}` : ''}`, {
        ...defaultOptions,
        autoClose: 4000
      });
    },

    warning: (message) => {
      toast.warning(message || 'Mail gönderilirken bir sorun oluştu', {
        ...defaultOptions,
        autoClose: 6000
      });
    },

    error: (error) => {
      toast.error(`Lütfen mail kutunuzu kontrol edin.: ${error}`, {
        ...defaultOptions,
        autoClose: 6000
      });
    },

    recipientNotFound: () => {
      toast.warning('Mail alıcısı bulunamadı. Lütfen IT ekibi ile iletişime geçin.', {
        ...defaultOptions,
        autoClose: 6000
      });
    },

    departmentNotFound: () => {
      toast.warning('NewCustomerForm_Mail departmanı bulunamadı. Lütfen IT ekibi ile iletişime geçin.', {
        ...defaultOptions,
        autoClose: 6000
      });
    }
  },

  // Form ve mail birleşik durumları için
  formAndMail: {
    completeSuccess: () => {
      toast.success('Form kaydedildi ve mail bildirimi gönderildi', {
        ...defaultOptions,
        autoClose: 4000
      });
    },

    partialSuccess: () => {
      toast.warning('Form kaydedildi fakat mail bildirimi gönderilemedi', {
        ...defaultOptions,
        autoClose: 6000
      });
    },

    processingWithMail: () => {
      toast.info('Form kaydediliyor ve mail bildirimi hazırlanıyor...', {
        ...defaultOptions,
        autoClose: 2000
      });
    }
  }
};

export default customerFormToasts;
