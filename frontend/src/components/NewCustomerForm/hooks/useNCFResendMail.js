// frontend/src/components/NewCustomerForm/hooks/useNCFResendMail.js
import { useState } from 'react';
import { resendFormMail } from '../../../api/mailservice';
import customerFormToasts from '../utils/toast';

const useNCFResendMail = (onSuccess) => {
  const [isResending, setIsResending] = useState(false);

  const resendMail = async (formId) => {
    if (!formId) {
      customerFormToasts.error('Form ID bulunamadı');
      return;
    }

    setIsResending(true);
    try {
      // Mail gönderme işlemini başlat
      customerFormToasts.mail.sending();

      const response = await resendFormMail(formId);

      if (response.success) {
        customerFormToasts.mail.success(response.message);
        
        // Başarılı gönderim sonrası callback fonksiyonunu çağır
        if (onSuccess && typeof onSuccess === 'function') {
          await onSuccess();
        }
      } else {
        customerFormToasts.mail.error(response.message || 'Mail gönderilemedi');
      }
    } catch (error) {
      console.error('Mail yeniden gönderme hatası:', error);
      customerFormToasts.mail.error(
        error.message || 'Mail gönderirken bir hata oluştu'
      );
    } finally {
      setIsResending(false);
    }
  };

  return {
    isResending,
    resendMail
  };
};

export default useNCFResendMail;