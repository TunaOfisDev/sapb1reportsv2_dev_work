// frontend/src/api/celery.js
import axiosInstance from './axiosconfig';

// Celery task durumunu kontrol etmek için fonksiyon
export const getTaskStatus = async (taskId) => {
  const response = await axiosInstance.get(`/rawmaterialwarehousestock/progress/${taskId}/`);
  return response.data;
};
