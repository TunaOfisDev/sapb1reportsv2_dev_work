// frontend/src/components/SalesOrderDocSum/utils/Toastify.js
import { toast } from 'react-toastify';

// Varsayılan konfigürasyon
const defaultConfig = {
  position: "top-right",
  autoClose: 5000,
  hideProgressBar: false,
  closeOnClick: true,
  pauseOnHover: true,
  draggable: true,
};

// Toast oluşturma fonksiyonu
const createToast = (message, type = "default", config = {}) => {
  const toastConfig = { ...defaultConfig, ...config };
  
  switch (type) {
    case "info":
      return toast.info(message, toastConfig);
    case "success":
      return toast.success(message, toastConfig);
    case "error":
      return toast.error(message, toastConfig);
    case "warning":
      return toast.warning(message, toastConfig);
    default:
      return toast(message, toastConfig);
  }
};

// Toastify nesnesi
const Toastify = {
  info: (message, config) => createToast(message, "info", config),
  success: (message, config) => createToast(message, "success", config),
  error: (message, config) => createToast(message, "error", config),
  warning: (message, config) => createToast(message, "warning", config),

  // Başlangıç yüklemeleri için Toast
  initialLoad: {
    start: () => createToast('Veriler yükleniyor, lütfen sayfayı kapatmayın...', "info", { autoClose: false }),
    success: () => {
      toast.dismiss();
      createToast('Veriler başarıyla yüklendi', "success");
    },
  },

  // Yerel veri çekme işlemi için Toast
  localDataFetch: {
    start: () => createToast('Yerel veriye bağlandı', "info"),
    success: () => createToast('Yerel veriden veriler başarı ile alındı', "success"),
  },

  // HANA DB veri çekme işlemi için Toast
  hanaDataFetch: {
    start: () => createToast('HANA DB ile bağlantı kuruldu, veriler alınıyor...', "info"),
    success: () => createToast('HANA DB\'den canlı veriler başarı ile alındı', "success"),
    error: () => createToast('HANA DB\'den veri alınırken bir hata oluştu', "error"),
  },

  // Tablo yenileme işlemi için Toast
  tableRefresh: {
    start: () => createToast('Tablo yenileniyor...', "info"),
    success: () => createToast('Tablo başarıyla güncellendi', "success"),
  },

  // HANA veri çekme ve tablo yenileme için Toast
  hanaDataFetchAndRefresh: {
    start: () => createToast('HANA verilerini çekme ve tablo yenileme işlemi başladı...', "info", { autoClose: false }),
    success: () => {
      toast.dismiss();
      createToast('HANA verileri alındı ve tablo güncellendi', "success");
    },
    error: () => createToast('HANA verilerini çekme veya tablo yenileme sırasında bir hata oluştu', "error"),
  },
};

export default Toastify;