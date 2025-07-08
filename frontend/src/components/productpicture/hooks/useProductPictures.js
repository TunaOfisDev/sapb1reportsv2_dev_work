// frontend/src/components/productpicture/hooks/useProductPictures.js
import { useState, useEffect, useCallback } from 'react';
import productPictureService from '../../../api/productpicture';

const useProductPictures = () => {
  const [productPictures, setProductPictures] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const fetchLocalData = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await productPictureService.fetchLocalData();
      setProductPictures(data || []);  // Veri yapısını güncelledik
      setLoading(false);
    } catch (err) {
      setError(err);
      setLoading(false);
    }
  };

  useEffect(() => {
    const fetchData = async () => {
      await fetchLocalData();
    };
    fetchData();
  }, []);

  const fetchInstantData = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await productPictureService.fetchInstantData();
      setProductPictures(data || []);  // Veri yapısını güncelledik
      setLoading(false);
    } catch (err) {
      setError(err);
      setLoading(false);
    }
  };


  // Resim URL'si oluşturma
  const getImageUrl = useCallback((filename) => {
    return productPictureService.getImageUrl(filename);
  }, []);

  useEffect(() => {
    fetchLocalData();
    
  }, []);

  return {
    productPictures,
    loading,
    error,
    fetchLocalData,
    fetchInstantData,
    getImageUrl,
   
  };
};

export default useProductPictures;
