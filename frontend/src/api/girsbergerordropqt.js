// frontend/src/api/girsbergerordropqt.js
import axiosInstance from './axiosconfig';

const getOrdrDetailOpqt = async () => {
  try {
    const response = await axiosInstance.get('girsbergerordropqt/ordr_detail_opqt/');
    return response.data; // 'results' anahtarına göre güncelleme
  } catch (error) {
    console.error('OrdrDetailOpqt verilerini getirirken bir hata oluştu:', error);
    throw error;
  }
};

const fetchHanaData = async () => {
  try {
    const response = await axiosInstance.get('girsbergerordropqt/fetch_hana_data/');
    return response.data;
  } catch (error) {
    console.error('HANA verilerini getirirken bir hata oluştu:', error);
    throw error;
  }
};

export { getOrdrDetailOpqt, fetchHanaData };
