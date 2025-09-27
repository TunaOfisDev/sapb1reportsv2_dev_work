// frontend/src/api/deliverydocsum.js
import axiosInstance from './axiosconfig';

const API_ENDPOINTS = {
  summaryList: '/deliverydocsum/summary-list/',
  fetchHana: '/deliverydocsum/fetch-hana/',
};

// Toplu doküman özetleri listesini çeken fonksiyon
export const fetchSummaryList = async () => {
  try {
    const response = await axiosInstance.get(API_ENDPOINTS.summaryList);
    return response.data; // Başarılı yanıt döndürüldüğünde veri döndürülüyor.
  } catch (error) {
    console.error('Error fetching summary list:', error);
    throw error; // Hata durumunda hata fırlatılıyor.
  }
};

// HANA veri tabanından veri çeken fonksiyon
export const fetchHanaData = async () => {
  try {
    const response = await axiosInstance.get(API_ENDPOINTS.fetchHana);
    return response.data; // Başarılı yanıt döndürüldüğünde veri döndürülüyor.
  } catch (error) {
    console.error('Error fetching HANA data:', error);
    throw error; // Hata durumunda hata fırlatılıyor.
  }
};
