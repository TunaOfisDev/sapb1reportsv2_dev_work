// frontend/src/components/NewCustomerForm/utils/formHelpers.js
export const getInitialFormData = () => ({
  firma_unvani: '',
  vergi_kimlik_numarasi: '',
  vergi_dairesi: '',
  firma_adresi: '',
  telefon_numarasi: '',
  email: '',
  muhasebe_irtibat_telefon: '',
  muhasebe_irtibat_email: '',
  odeme_sartlari: '',
  iskonto_anlasmasi: '',
  vergi_levhasi: null,
  faaliyet_belgesi: null,
  ticaret_sicil: null,
  imza_sirkuleri: null,
  banka_iban: null,
  yetkili_kisiler: []
});

const REQUIRED_FIELDS = {
  firma_unvani: 'Firma ünvanı zorunludur',
  vergi_kimlik_numarasi: 'Vergi kimlik numarası zorunludur',
  vergi_dairesi: 'Vergi dairesi zorunludur',
  firma_adresi: 'Firma adresi zorunludur',
  telefon_numarasi: 'Telefon numarası zorunludur',
  email: 'E-posta adresi zorunludur',
  muhasebe_irtibat_telefon: 'Muhasebe irtibat telefonu zorunludur',
  muhasebe_irtibat_email: 'Muhasebe irtibat e-postası zorunludur',
  odeme_sartlari: 'Ödeme şartları zorunludur'
};

const VKN_REGEX = /^\d{10,11}$/;
const EMAIL_REGEX = /^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$/i;
const PHONE_REGEX = /^[0-9]{10,11}$/;
const FILE_SIZE_LIMIT = 1024 * 1024;

export const validateForm = (formData) => {
  const newErrors = {};

  // Zorunlu alan kontrolleri
  Object.entries(REQUIRED_FIELDS).forEach(([field, message]) => {
    if (!formData[field]?.trim()) {
      newErrors[field] = message;
    }
  });

  // VKN validasyonu
  if (formData.vergi_kimlik_numarasi && !VKN_REGEX.test(formData.vergi_kimlik_numarasi)) {
    newErrors.vergi_kimlik_numarasi = 'Geçerli bir vergi kimlik numarası giriniz';
  }

  // Email validasyonları
  const validateEmail = (email) => email && !EMAIL_REGEX.test(email);
  if (validateEmail(formData.email)) newErrors.email = 'Geçerli bir e-posta adresi giriniz';
  if (validateEmail(formData.muhasebe_irtibat_email)) {
    newErrors.muhasebe_irtibat_email = 'Geçerli bir e-posta adresi giriniz';
  }

  // Telefon validasyonları
  const validatePhone = (phone) => phone && !PHONE_REGEX.test(phone.replace(/\D/g, ''));
  if (validatePhone(formData.telefon_numarasi)) newErrors.telefon_numarasi = 'Geçerli bir telefon numarası giriniz';
  if (validatePhone(formData.muhasebe_irtibat_telefon)) {
    newErrors.muhasebe_irtibat_telefon = 'Geçerli bir telefon numarası giriniz';
  }

  // Dosya validasyonları
  const fileFields = ['vergi_levhasi', 'faaliyet_belgesi', 'ticaret_sicil', 'imza_sirkuleri', 'banka_iban'];
  fileFields.forEach(field => {
    const file = formData[field];
    if (file instanceof File && file.size > FILE_SIZE_LIMIT) {
      newErrors[field] = 'Dosya boyutu 1MB\'dan küçük olmalıdır';
    }
  });

 // Yetkili kişi validasyonları - OPSİYONEL!
 if (formData.yetkili_kisiler.length > 0) {
  const yetkiliErrors = [];
  let hasValidEntry = false;

  formData.yetkili_kisiler.forEach((kisi, index) => {
    const kisininHatalari = [];
    const hasAnyField = kisi.ad_soyad?.trim() || kisi.telefon?.trim() || kisi.email?.trim();

    // Eğer herhangi bir alan doldurulduysa diğerlerini kontrol et
    if (hasAnyField) {
      if (!kisi.ad_soyad?.trim()) {
        kisininHatalari.push('Ad soyad zorunludur');
      }
      if (!kisi.telefon?.trim()) {
        kisininHatalari.push('Telefon zorunludur');
      } else if (validatePhone(kisi.telefon)) {
        kisininHatalari.push('Geçerli bir telefon numarası giriniz');
      }
      if (!kisi.email?.trim()) {
        kisininHatalari.push('E-posta zorunludur');
      } else if (validateEmail(kisi.email)) {
        kisininHatalari.push('Geçerli bir e-posta adresi giriniz');
      }

      // Eğer hiç hata yoksa, geçerli bir kayıt var demektir
      if (kisininHatalari.length === 0) {
        hasValidEntry = true;
      }
    }

    if (kisininHatalari.length > 0) {
      yetkiliErrors[index] = kisininHatalari.join(', ');
    }
  });

  // Eğer yetkili kişi girişi yapılmışsa ve hiç geçerli kayıt yoksa hata göster
  if (yetkiliErrors.length > 0 && !hasValidEntry) {
    newErrors.yetkili_kisiler = yetkiliErrors;
  }
}

return newErrors;
};

export const validateFileSize = (file) => {
  if (file?.size > FILE_SIZE_LIMIT) return 'Dosya boyutu 1MB\'dan küçük olmalıdır';
  return null;
};