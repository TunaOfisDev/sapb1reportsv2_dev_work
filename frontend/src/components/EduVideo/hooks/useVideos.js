// frontend/src/components/EduVideo/hooks/useVideos.js
import { useState, useEffect } from 'react';
import axios from '../../../api/axiosconfig';

const useVideos = () => {
  const [videos, setVideos] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [pageIndex, setPageIndex] = useState(0);
  const [pageSize, setPageSize] = useState(1000); 

  useEffect(() => {
    const fetchVideos = async () => {
      setLoading(true);
      setError(null);
      try {
        const response = await axios.get('/eduvideo/videos/');
        setVideos(response.data); // Doğrudan API'den gelen veriyi kullan
      } catch (err) {
        setError('Veri yüklenirken bir hata oluştu');
        console.error('API hatası:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchVideos();
  }, []);

  // Toplam sayfa sayısını hesaplayın
  const pageCount = Math.ceil(videos.length / pageSize);

  // Sayfa değiştirme işlevi
  const handlePageChange = (newPageIndex) => {
    setPageIndex(newPageIndex);
  };

  // Sayfa boyutunu güncelleyen işlev
  const handlePageSizeChange = (newSize) => {
    setPageSize(newSize);
    setPageIndex(0); // Sayfa boyutu değiştikten sonra ilk sayfaya dön
  };

  // İlk görünen videoları seçin
  const paginatedVideos = videos.slice(
    pageIndex * pageSize,
    (pageIndex + 1) * pageSize
  );

  return {
    videos: paginatedVideos,
    loading,
    error,
    pageIndex,
    handlePageChange,
    pageCount,
    pageSize,
    handlePageSizeChange,
  };
};

export default useVideos;