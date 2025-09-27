// frontend/src/api/supplierpayment.js
import axiosInstance from './axiosconfig';

const getLocalDbSupplierPayments = async () => {
  try {
    const response = await axiosInstance.get('supplierpayment/local_db_closing_invoice');
    return response.data;
  } catch (error) {
    console.error('Error fetching local DB supplier payments:', error);
    throw error;
  }
};

const fetchHanaDbCombinedService = async () => {
  try {
    const response = await axiosInstance.get('supplierpayment/fetch_hana_db_combined_service/');
    const { task_id } = response.data;
    return task_id;
  } catch (error) {
    console.error('Error fetching HANA DB combined service data:', error);
    throw error;
  }
};

const getLastUpdatedTime = async () => {
  try {
    const response = await axiosInstance.get('supplierpayment/last_updated_supplier_payment/');
    console.log('API Response:', response); // Debug için
    return response.data;
  } catch (error) {
    console.error('Error fetching the last updated time:', error);
    throw error;
  }
};

const getTaskStatus = async (taskId) => {
  try {
    const response = await axiosInstance.get(`supplierpayment/task_status/${taskId}/`);
    return response.data;
  } catch (error) {
    console.error('Error fetching task status:', error);
    throw error;
  }
};

// Yeni endpoint için fonksiyon
const fetchHanaDb = async () => {
  try {
    const response = await axiosInstance.get('supplierpayment/fetch_hana_db/');
    // Başarılı yanıt
    if (response.data.status === 'success') {
      return {
        status: 'success',
        message: response.data.message,
        details: response.data.details
      };
    }
    // Veri bulunamadı durumu
    return {
      status: 'no_data',
      message: response.data.message || 'HANA veritabanında yeni veri bulunmamaktadır.',
      details: response.data.details
    };
  } catch (error) {
    console.error('Error fetching HANA DB data:', error);
    // API'den gelen hata mesajını kullan
    if (error.response?.data) {
      return {
        status: 'error',
        message: error.response.data.message || 'Beklenmeyen bir hata oluştu.',
        details: error.response.data.details
      };
    }
    // Bağlantı hatası durumu
    if (error.request) {
      return {
        status: 'error',
        message: 'Sunucuya bağlanılamadı. Lütfen internet bağlantınızı kontrol edin.'
      };
    }
    // Diğer hatalar
    return {
      status: 'error',
      message: 'Bir hata oluştu. Lütfen daha sonra tekrar deneyin.'
    };
  }
};

// WebSocket bağlantısı ve mesaj işleyici
const createWebSocketConnection = (onMessage) => {
  const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
  const host = window.location.host;
  const wsUrl = `${wsProtocol}//${host}/ws/supplierpayment/`;
  
  try {
    const socket = new WebSocket(wsUrl);
    
    socket.onopen = () => {
      console.log('WebSocket bağlantısı başarılı');
    };
    
    socket.onmessage = (e) => {
      try {
        const data = JSON.parse(e.data);
        if (onMessage) {
          onMessage(data.message);
        }
      } catch (error) {
        console.error('WebSocket mesaj işleme hatası:', error);
      }
    };
    
    socket.onerror = (error) => {
      console.error('WebSocket hatası:', error);
    };

    socket.onclose = () => {
      console.log('WebSocket bağlantısı kapandı');
      setTimeout(() => createWebSocketConnection(onMessage), 5000);
    };

    return socket;
  } catch (error) {
    console.error('WebSocket bağlantı hatası:', error);
    return null;
  }
};

const supplierpayment = {
  getLocalDbSupplierPayments,
  fetchHanaDbCombinedService,
  getLastUpdatedTime,
  getTaskStatus,
  fetchHanaDb, 
  createWebSocketConnection,  
};

export default supplierpayment;