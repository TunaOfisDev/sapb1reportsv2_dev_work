// frontend/src/api/mailservice.js
import axiosInstance from './axiosconfig';

/**
* Tüm mail loglarını getirir.
* @returns {Promise<object[]>} - Mail loglarının listesini döndürür.
*/
export const getAllMailLogs = async () => {
 try {
   console.log('getAllMailLogs servisi çağrıldı');
   const response = await axiosInstance.get('mailservice/logs/');
   console.log('getAllMailLogs servis yanıtı:', {
     status: response.status,
     data: response.data,
     count: response.data?.results?.length || 0
   });
   return response.data;
 } catch (error) {
   console.error('getAllMailLogs servisi hatası:', {
     message: error.message,
     response: error.response?.data,
     status: error.response?.status
   });
   throw error;
 }
};

/**
* Mail loglarını form ID'ye göre filtreli getirir.
* @param {number} formId - Form ID
* @returns {Promise<object[]>} - Mail loglarının listesini döndürür.
*/
export const getFormMailLogs = async (formId) => {
 try {
   console.log('getFormMailLogs servisi çağrıldı:', { formId });
   const response = await axiosInstance.get('mailservice/logs/', { 
     params: {
       related_object_type: 'NewCustomerForm',
       related_object_id: formId
     }
   });
   console.log('getFormMailLogs servis yanıtı:', {
     formId,
     status: response.status,
     data: response.data,
     count: response.data?.results?.length || 0
   });
   return response.data;
 } catch (error) {
   console.error('getFormMailLogs servisi hatası:', {
     formId,
     message: error.message,
     response: error.response?.data,
     status: error.response?.status
   });
   throw error;
 }
};

/**
* Belirli bir form için mail gönderimini yeniden dener.
* @param {number} formId - Form ID
* @returns {Promise<object>} - Yeniden gönderim sonucunu döndürür.
*/
export const resendFormMail = async (formId) => {
  try {
    console.log('Mail gönderme isteği başlatıldı - Form ID:', formId);

    const response = await axiosInstance.post('mailservice/logs/resend-mail/', {
      related_object_id: formId
    });

    console.log('Mail gönderme yanıtı:', response.data);

    if (response.data.success) {
      return {
        success: true,
        message: response.data.message || 'Mail başarıyla gönderildi'
      };
    } else {
      throw new Error(response.data.message || 'Mail gönderilemedi');
    }
  } catch (error) {
    console.error('Mail gönderme hatası:', {
      formId,
      error: error.response?.data || error.message
    });
    throw {
      success: false,
      message: error.response?.data?.message || error.message || 'Mail gönderilemedi',
      error: error.response?.data || error
    };
  }
};