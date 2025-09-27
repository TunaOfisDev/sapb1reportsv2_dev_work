// frontend/src/api/deliverydocsumv2.js
import axiosInstance from './axiosconfig';

const API_ENDPOINTS = {
  summaryList: '/deliverydocsumv2/summary-list/',
  fetchHana: '/deliverydocsumv2/fetch-hana/',
  dynamicNameColumns: '/deliverydocsumv2/dynamic-name-columns/',  // Yeni endpoint
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

// Dinamik kolon isimlerini çeken fonksiyon
export const fetchDynamicNameColumns = async () => {
  try {
    const response = await axiosInstance.get(API_ENDPOINTS.dynamicNameColumns);
    return response.data; // Başarılı yanıt döndürüldüğünde veri döndürülüyor.
  } catch (error) {
    console.error('Error fetching dynamic name columns:', error);
    throw error; // Hata durumunda hata fırlatılıyor.
  }
};

