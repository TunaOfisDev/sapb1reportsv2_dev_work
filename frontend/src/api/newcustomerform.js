// frontend/src/api/newcustomerform.js
import axiosInstance from './axiosconfig';

// Yeni müşteri formu oluşturma fonksiyonu (değişmedi)
export const createNewCustomerForm = async (data) => {
  try {
    const formData = new FormData();

    // Form verilerini ekle
    const basicFields = [
      'firma_unvani',
      'vergi_kimlik_numarasi',
      'vergi_dairesi',
      'firma_adresi',
      'telefon_numarasi',
      'email',
      'muhasebe_irtibat_telefon',
      'muhasebe_irtibat_email',
      'odeme_sartlari',
      'iskonto_anlasmasi'
    ];

    basicFields.forEach(field => {
      if (data[field]) {
        formData.append(field, data[field]);
      }
    });

    // Dosyaları ekle
    const fileFields = [
      'vergi_levhasi',
      'faaliyet_belgesi',
      'ticaret_sicil',
      'imza_sirkuleri',
      'banka_iban'
    ];

    fileFields.forEach(field => {
      if (data[field] instanceof File) {
        formData.append(field, data[field]);
      }
    });

    // Yetkili kişileri ekle (varsa)
    if (Array.isArray(data.yetkili_kisiler) && data.yetkili_kisiler.length > 0) {
      const validYetkiliKisiler = data.yetkili_kisiler.filter(kisi =>
        kisi.ad_soyad?.trim() &&
        kisi.telefon?.trim() &&
        kisi.email?.trim()
      );
      
      if (validYetkiliKisiler.length > 0) {
        formData.append('yetkili_kisiler', JSON.stringify(validYetkiliKisiler));
      }
    }

    // API çağrısını yap (mail gönderimi senkron şekilde yapılıyor)
    const response = await axiosInstance.post('newcustomerform/', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    });

    // API yanıtı, mail_status alanı ile birlikte dönecek.
    return response.data;

  } catch (error) {
    console.error('Form gönderim hatası:', error);
    throw {
      status: error.response?.status || 500,
      data: error.response?.data || {},
      message: error.response?.data?.detail || error.message || 'Form gönderiminde bir hata oluştu',
      config: error.config
    };
  }
};

// Dashboard: Oturum açan kullanıcının oluşturduğu formları listeleme fonksiyonu
export const getUserNewCustomerForms = async () => {
  try {
    console.log('getUserNewCustomerForms servisi çağrıldı');
    const response = await axiosInstance.get('newcustomerform/list/');
    console.log('getUserNewCustomerForms servis yanıtı:', {
      status: response.status,
      data: response.data,
      results: response.data.results,
      count: response.data?.results?.length || 0
    });
    
    // Form listesi boş kontrolü
    if (!response.data?.results?.length) {
      console.warn('Form listesi boş döndü');
    }

    // Form yapısını kontrol et
    if (response.data?.results?.length > 0) {
      console.log('İlk form örneği:', response.data.results[0]);
    }

    return response.data.results; 
  } catch (error) {
    console.error('getUserNewCustomerForms servisi hatası:', {
      message: error.message,
      response: error.response?.data,
      status: error.response?.status,
      config: error.config
    });
    throw error;
  }
};

// Dashboard: Belirli bir formu getirme fonksiyonu
export const retrieveUserNewCustomerForm = async (id) => {
  try {
    console.log('Form detayları getiriliyor:', id);
    const response = await axiosInstance.get(`newcustomerform/${id}/`);
    console.log('Form detayları:', response.data);
    return response.data;
  } catch (error) {
    console.error('Form detayları alınırken hata:', error);
    throw error;
  }
};

export const updateUserNewCustomerForm = async (id, data) => {
  try {
    console.log('Form güncelleniyor:', { id, data });
    const formData = new FormData();
    
    // Temel alanları ekle
    const basicFields = [
      'firma_unvani',
      'vergi_kimlik_numarasi',
      'vergi_dairesi',
      'firma_adresi',
      'telefon_numarasi',
      'email',
      'muhasebe_irtibat_telefon',
      'muhasebe_irtibat_email',
      'odeme_sartlari',
      'iskonto_anlasmasi'
    ];

    basicFields.forEach(field => {
      if (data[field] !== undefined && data[field] !== null) {
        formData.append(field, data[field]);
      }
    });

    // Dosya alanlarını kontrol et
    const fileFields = [
      'vergi_levhasi',
      'faaliyet_belgesi',
      'ticaret_sicil',
      'imza_sirkuleri',
      'banka_iban'
    ];

    fileFields.forEach(field => {
      if (data[field] instanceof File) {
        formData.append(field, data[field]);
      }
      // Mevcut dosya URL'i veya null ise gönderme
    });

    // Yetkili kişileri ekle
    if (Array.isArray(data.yetkili_kisiler) && data.yetkili_kisiler.length > 0) {
      const validYetkiliKisiler = data.yetkili_kisiler.filter(kisi =>
        kisi.ad_soyad?.trim() &&
        kisi.telefon?.trim() &&
        kisi.email?.trim()
      );
      
      if (validYetkiliKisiler.length > 0) {
        formData.append('yetkili_kisiler', JSON.stringify(validYetkiliKisiler));
      }
    }

    const response = await axiosInstance.patch(
      `newcustomerform/${id}/`, 
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      }
    );
    
    console.log('Form güncelleme yanıtı:', response.data);
    return response.data;
  } catch (error) {
    console.error('Form güncellenirken hata:', error);
    throw error;
  }
};