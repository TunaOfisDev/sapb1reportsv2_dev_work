// frontend/src/api/crmblog.js
import axiosInstance from './axiosconfig';

// Tüm görevleri listele
export const getAllPosts = async () => {
  try {
    const response = await axiosInstance.get('/crmblog/posts/');
    return response.data;
  } catch (error) {
    const errorMessage = error.response?.data?.detail || 'Görevleri getirme sırasında bir hata oluştu. Lütfen tekrar deneyin.';
    throw new Error(errorMessage); // Hata mesajını doğru şekilde döndürüyoruz
  }
};

// Belirli bir görevi getir
export const getPostById = async (id) => {
  try {
    const response = await axiosInstance.get(`/crmblog/posts/${id}/`);
    return response.data;
  } catch (error) {
    const errorMessage = error.response?.data?.detail || `ID'si ${id} olan görevi getirirken bir hata oluştu.`;
    throw new Error(errorMessage);
  }
};

// Yeni bir görev oluştur
export const createPost = async (postData) => {
  try {
    const response = await axiosInstance.post('/crmblog/posts/', postData);
    return response.data;
  } catch (error) {
    const errorMessage = error.response?.data?.detail || 'Yeni görev oluştururken bir hata oluştu. Lütfen tekrar deneyin.';
    throw new Error(errorMessage);
  }
};

// Görevi güncelle
export const updatePost = async (id, postData) => {
  try {
    const response = await axiosInstance.put(`/crmblog/posts/${id}/`, postData);
    return response.data;
  } catch (error) {
    const errorMessage = error.response?.data?.detail || `ID'si ${id} olan görevi güncellerken bir hata oluştu.`;
    throw new Error(errorMessage);
  }
};

// Görevi sil
export const deletePost = async (id) => {
  try {
    const response = await axiosInstance.delete(`/crmblog/posts/${id}/`);
    return response.data;
  } catch (error) {
    const errorMessage = error.response?.data?.detail || `ID'si ${id} olan görevi silerken bir hata oluştu.`;
    throw new Error(errorMessage);
  }
};
