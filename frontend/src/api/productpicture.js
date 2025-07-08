// frontend/src/api/productpicture.js
import axiosInstance from './axiosconfig';

const fetchInstantData = async () => {
  try {
    const response = await axiosInstance.get('productpicture/fetch-hana-data/');  
    return response.data;
  } catch (error) {
    console.error("HANA DB veri çekme hatası", error.response || error);
    throw error;
  }
};

const fetchLocalData = async () => {
  try {
    const response = await axiosInstance.get('productpicture/products/'); 
    return response.data;
  } catch (error) {
    console.error("Yerel DB veri çekme hatası", error.response || error);
    throw error;
  }
};


// Resim URL'si almak için güncellenmiş fonksiyon
const getImageUrl = (picturePath) => {
  // Backend tarafından dönen tam resim yolu doğrudan kullanılır
  return picturePath;
};



const productPictureService = {
  fetchInstantData,
  fetchLocalData,
  getImageUrl,  
};

export default productPictureService;
