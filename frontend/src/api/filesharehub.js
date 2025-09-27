// frontend/src/api/filesharehub.js
import axiosInstance from './axiosconfig';

// Dosya ve klasörleri listeleme API'si
export const getFileList = async (directoryPath = '') => {
  try {
    const encodedPath = encodeURIComponent(directoryPath);
    const response = await axiosInstance.get(`filesharehub/files/${encodedPath}`);
    return response.data;
  } catch (error) {
    console.error('Dosya listesi alınırken hata oluştu:', error);
    throw error;
  }
};

// Dosya indirme API'si
export const downloadFile = async (filename, path = '') => {
  try {
    const encodedFilename = encodeURIComponent(filename);
    const encodedPath = path ? encodeURIComponent(path) + '/' : '';
    const response = await axiosInstance.get(`filesharehub/files/${encodedPath}${encodedFilename}`, {
      responseType: 'blob',
    });
    const url = window.URL.createObjectURL(new Blob([response.data]));
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', filename);
    document.body.appendChild(link);
    link.click();
    link.remove();
  } catch (error) {
    console.error(`${filename} dosyası indirilirken hata oluştu:`, error);
    throw error;
  }
};

