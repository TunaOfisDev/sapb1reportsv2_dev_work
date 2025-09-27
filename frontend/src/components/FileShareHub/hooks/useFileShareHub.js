// frontend/src/components/FileShareHub/hooks/useFileShareHub.js
import { useState, useEffect, useCallback } from 'react';
import { getFileList, downloadFile } from '../../../api/filesharehub'; // getFileThumbnail fonksiyonunu kaldırdık

const useFileShareHub = () => {
  const [path, setPath] = useState('');
  const [contents, setContents] = useState({ directories: [], files: [] });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const loadDirectory = useCallback(async (directoryPath = '') => {
    setLoading(true);
    setError(null);
    try {
      const data = await getFileList(directoryPath);
      setContents(data);
      setPath(directoryPath);
    } catch (error) {
      console.error('Dosya listesi yüklenirken hata:', error);
      setError(`Dosya listesi yüklenirken hata: ${error.response?.data?.detail || error.message}`);
    } finally {
      setLoading(false);
    }
  }, []);

  const handleFileDownload = useCallback(async (filename) => {
    try {
      await downloadFile(filename, path);
    } catch (error) {
      setError(`${filename} dosyası indirilirken bir hata oluştu.`);
    }
  }, [path]);

  useEffect(() => {
    loadDirectory();
  }, [loadDirectory]);

  return { 
    path, 
    contents, 
    loading, 
    error, 
    loadDirectory, 
    handleFileDownload, 
    setPath 
  };
};

export default useFileShareHub;
