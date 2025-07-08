// frontend/src/api/eduvideo.js
import axiosInstance from './axiosconfig';

export const getEduVideos = async () => {
  try {
    const response = await axiosInstance.get(`eduvideo/videos/`); 
    return response.data;
  } catch (error) {
    console.error('EduVideo servisinde bir hata meydana geldi:', error);
    throw error;
  }
};
