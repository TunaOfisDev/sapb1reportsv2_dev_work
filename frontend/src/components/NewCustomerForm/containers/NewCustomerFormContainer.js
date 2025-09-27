// frontend/src/components/NewCustomerForm/containers/NewCustomerFormContainer.js
import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { ToastContainer, toast } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import NewCustomerForm from '../forms/NewCustomerForm';

const NewCustomerFormContainer = () => {
  const navigate = useNavigate();
  const [isSubmitting, setIsSubmitting] = useState(false);

  useEffect(() => {
    document.title = 'Yeni Müşteri Başvuru Formu';
    return () => {
      document.title = 'Panel';
    };
  }, []);

  const handleFormSuccess = (response) => {
    setIsSubmitting(true);
    
    // Mail durumunu kontrol et
    const mailStatus = response?.mail_status || {};
    
    // Başarı toast bildirimi göster
    if (mailStatus.sent) {
      toast.success('Form başarıyla kaydedildi ve mail gönderildi!', {
        position: "top-right",
        autoClose: 3000,
        hideProgressBar: false,
        closeOnClick: true,
        pauseOnHover: true,
        draggable: true,
        progress: undefined,
      });
    } else {
      toast.warning('Form kaydedildi. Lütfen mail kutunuzu kontrol edin..', {
        position: "top-right",
        autoClose: 3000,
        hideProgressBar: false,
        closeOnClick: true,
        pauseOnHover: true,
        draggable: true,
        progress: undefined,
      });
    }

    // 3 saniye sonra dashboard'a yönlendir
    setTimeout(() => {
      navigate('/newcustomerform', {
        state: {
          notification: {
            type: 'success',
            message: 'Yeni müşteri başvurunuz başarıyla alınmıştır.'
          }
        }
      });
    }, 3000);
  };

  const handleFormError = (error) => {
    console.error('Form gönderim hatası:', error);
    setIsSubmitting(false);

    // API'den gelen hata mesajlarını kontrol et
    let errorMessage = 'Form gönderilirken bir hata oluştu!';
    
    if (error.response?.data) {
      if (typeof error.response.data === 'object') {
        // Validasyon hataları için
        const errors = Object.entries(error.response.data)
          .map(([field, messages]) => `${field}: ${messages.join(', ')}`)
          .join('\n');
        errorMessage = errors || errorMessage;
      } else if (error.response.data.detail) {
        errorMessage = error.response.data.detail;
      } else if (typeof error.response.data === 'string') {
        errorMessage = error.response.data;
      }
    } else if (error.message) {
      errorMessage = error.message;
    }

    // Hata toast bildirimi göster
    toast.error(errorMessage, {
      position: "top-right",
      autoClose: 5000,
      hideProgressBar: false,
      closeOnClick: true,
      pauseOnHover: true,
      draggable: true,
      progress: undefined,
    });
  };

  return (
    <div className="container mx-auto px-4 py-8">
      {/* Toast Container */}
      <ToastContainer
        position="top-right"
        autoClose={5000}
        hideProgressBar={false}
        newestOnTop
        closeOnClick
        rtl={false}
        pauseOnFocusLoss
        draggable
        pauseOnHover
        theme="light"
      />

      <div className="max-w-4xl mx-auto">
        {/* Sayfa Başlığı */}
        <div className="mb-8 text-center">
          <h1 className="text-2xl font-bold text-gray-800 mb-2">
            Yeni Müşteri Başvuru Formu
          </h1>
          <p className="mt-2 text-gray-600">
            Lütfen aşağıdaki formu eksiksiz doldurunuz. Tüm alanlar zorunludur.
            Tüm dosyalar en fazla 1MB boyutunda olabilir.
            Dosyalar PDF, JPG veya PNG formatında olmalıdır.
            Form gönderildikten sonra başvurunuz incelenecek ve size e-posta ile bilgi verilecektir.
            Eksik veya hatalı bilgi içeren başvurular değerlendirmeye alınmayacaktır. -Tuna Ofis AŞ Muhasebe Departmani 
          </p>
        </div>

        {/* Form Kartı */}
        <div className="bg-white rounded-lg shadow-lg">
          <NewCustomerForm 
            onSuccess={handleFormSuccess}
            onError={handleFormError}
            isSubmitting={isSubmitting}
          />
        </div>

        {/* Bilgilendirme Notları */}
        <div className="mt-8 p-4 bg-blue-50 rounded-lg">
          <h2 className="text-lg font-semibold text-blue-800 mb-2">
            Önemli Bilgiler
          </h2>
          <ul className="list-disc list-inside text-blue-700 space-y-2">
            <li>
              Tüm dosyalar en fazla 1MB boyutunda olabilir.
            </li>
            <li>
              Dosyalar PDF, JPG veya PNG formatında olmalıdır.
            </li>
            <li>
              Form gönderildikten sonra başvurunuz incelenecek ve size e-posta ile bilgi verilecektir.
            </li>
            <li>
              Eksik veya hatalı bilgi içeren başvurular değerlendirmeye alınmayacaktır.
            </li>
          </ul>
        </div>

        {/* Loading Overlay */}
        {isSubmitting && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
            <div className="bg-white p-4 rounded-lg shadow-lg">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500 mx-auto"></div>
              <p className="mt-2 text-center text-gray-700">Form gönderiliyor...</p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default NewCustomerFormContainer;