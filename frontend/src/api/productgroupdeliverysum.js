// frontend/src/api/productgroupdeliverysum.js
import axiosInstance from './axiosconfig';

// Yerel veritabanındaki Product Group Delivery Summary verilerini çekme fonksiyonu
export const fetchLocalData = async () => {
  try {
    const response = await axiosInstance.get('productgroupdeliverysum/local-data/');
    return response.data; // Başarılı yanıtı döndür
  } catch (error) {
    // Hata durumunda error objesini döndür
    console.error('Product Group Delivery Summary Fetching Error:', error.response || error);
    throw error;
  }
};

// HANA DB'den veri çekme ve veritabanını güncelleme fonksiyonu
export const fetchHanaData = async () => {
  try {
    const response = await axiosInstance.get('productgroupdeliverysum/fetch-hana/');
    return response.data; // Başarılı yanıtı döndür
  } catch (error) {
    // Hata durumunda error objesini döndür
    console.error('Fetch HANA Data Error:', error.response || error);
    throw error;
  }
};

// Yıl bazlı karşılaştırma verilerini çekme fonksiyonu
export const fetchYearComparisonData = async (year) => {
  try {
    const response = await axiosInstance.get(`productgroupdeliverysum/year-comparison/${year}/`);
    return response.data; // { currentYear: [...], previousYear: [...] } şeklinde veri döner
  } catch (error) {
    console.error('Year Comparison Data Fetching Error:', error.response || error);
    throw error;
  }
};

// Şu anki yıl için karşılaştırma verilerini getiren yardımcı fonksiyon
export const fetchCurrentYearComparison = async () => {
  const currentYear = new Date().getFullYear();
  return fetchYearComparisonData(currentYear);
};