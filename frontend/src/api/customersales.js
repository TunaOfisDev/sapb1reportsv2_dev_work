// frontend/src/api/customersales.js
import axiosInstance from './axiosconfig';

const getCustomerSalesOrders = async () => {
  try {
    const response = await axiosInstance.get('salesorder/customer-salesorders/');
    return response.data;
  } catch (error) {
    console.error('Error fetching customer sales orders:', error);
    throw error;
  }
};

const fetchHanaCustomerSalesData = async () => {
  try {
    const response = await axiosInstance.get('salesorder/fetch-hana-customersales-data/');
    return response.data;
  } catch (error) {
    console.error('Error fetching HANA customer sales data:', error);
    throw error;
  }
};

// En son güncellenme tarihini ve saatini almak için yeni bir fonksiyon
const getLastUpdatedTime = async () => {
  try {
    const response = await axiosInstance.get('salesorder/last-updated/');
    // API'den gelen `last_updated` değerini doğrudan döndürüyoruz.
    return response.data.last_updated;
  } catch (error) {
    console.error('Error fetching the last updated time:', error);
    throw error;
  }
};

const exportCustomerSalesToXLSX = async () => {
  try {
    // Export endpoint'ine GET isteği gönderin
    const response = await axiosInstance.get('salesorder/export-xlsx/', { responseType: 'blob' });

    // Blob oluştur
    const blob = new Blob([response.data], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' });

    // Blob URL oluştur
    const url = window.URL.createObjectURL(blob);

    // Dosyayı indirme bağlantısını oluştur
    const link = document.createElement('a');
    link.href = url;
    link.download = 'customer_sales_orders.xlsx';

    // Dosyayı indirme bağlantısını tıklama
    link.click();

    // Blob URL'yi temizle
    window.URL.revokeObjectURL(url);
  } catch (error) {
    console.error('Error exporting customer sales to XLSX:', error);
    throw error;
  }
};

const customersales = {
  getCustomerSalesOrders,
  fetchHanaCustomerSalesData,
  getLastUpdatedTime,
  exportCustomerSalesToXLSX
};

export default customersales;
