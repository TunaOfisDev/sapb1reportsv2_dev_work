// frontend/src/api/tunainssupplieradvancebalance.js
import axiosInstance from './axiosconfig';

const fetchLocalData = async () => {
  try {
    const response = await axiosInstance.get('tunainssupplieradvancebalance/total-risk/');
    return response.data; // Başarılı yanıt döndür
  } catch (error) {
    // Hata durumunda error objesini döndür
    console.error('Total Risk Reports Fetching Error:', error.response || error);
    throw error;
  }
};

const fetchHanaData = async () => {
  try {
    const response = await axiosInstance.get('tunainssupplieradvancebalance/fetch-hana-data/');
    return response.data; // Başarılı yanıt döndür
  } catch (error) {
    // Hata durumunda error objesini döndür
    console.error('Fetch HANA Data Error:', error.response || error);
    throw error;
  }
};

// En son güncellenme tarihini ve saatini almak için yeni bir fonksiyon
const getLastUpdatedTime = async () => {
  try {
    const response = await axiosInstance.get('tunainssupplieradvancebalance/last-updated/');
    // API'den gelen `last_updated` değerini doğrudan döndürüyoruz.
    return response.data.last_updated;
  } catch (error) {
    console.error('Error fetching the last updated time:', error);
    throw error;
  }
};

const exportTotalRiskToXLSX = async () => {
  try {
    const response = await axiosInstance.get('tunainssupplieradvancebalance/export-xlsx/', { responseType: 'blob' });
    
    const blob = new Blob([response.data], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' });
    
    const url = window.URL.createObjectURL(blob);
    
    const link = document.createElement('a');
    link.href = url;
    link.download = 'total_risk_report.xlsx';
    
    link.click();
    
    window.URL.revokeObjectURL(url);
  } catch (error) {
    console.error('Error exporting total risk to XLSX:', error);
    throw error;
  }
};

export { fetchLocalData, fetchHanaData, getLastUpdatedTime, exportTotalRiskToXLSX };
