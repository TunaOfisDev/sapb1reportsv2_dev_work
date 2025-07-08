// frontend/src/components/CrmBlog/hooks/useCrmBlog.js
import { useState, useEffect, useCallback } from 'react';
import { getAllPosts, getPostById, createPost, updatePost, deletePost } from '../../../api/crmblog';

// Custom hook for CRM blog operations
const useCrmBlog = () => {
  const [posts, setPosts] = useState([]);
  const [post, setPost] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // Genel hata mesajı yönetimi
  const handleError = (error) => {
    // Eğer backend'den gelen spesifik bir hata varsa onu gösterelim
    if (error.response && error.response.data && error.response.data.detail) {
      setError(error.response.data.detail); // Backend'den dönen Türkçe hata mesajı
    } else if (error.message) {
      setError(error.message); // Axios tarafından dönen hata mesajı
    } else {
      setError('Bir hata oluştu. Lütfen tekrar deneyin.'); // Genel hata mesajı
    }
  };

  // Tüm görevleri getir
  const fetchPosts = useCallback(async () => {
    setLoading(true);
    setError(null); // Önceki hataları sıfırla
    try {
      const data = await getAllPosts();
      setPosts(data.results);
    } catch (error) {
      handleError(error); // Hata yönetimini çağırıyoruz
    } finally {
      setLoading(false);
    }
  }, []);

  // Belirli bir görevi ID ile getir
  const fetchPost = useCallback(async (id) => {
    setLoading(true);
    setError(null);
    try {
      const post = await getPostById(id);
      setPost(post);
    } catch (error) {
      handleError(error);
      throw error; // Hata durumunda hata fırlatıyoruz
    } finally {
      setLoading(false);
    }
  }, []);

  // Yeni bir görev oluştur
  const addPost = useCallback(async (postData) => {
    setLoading(true);
    setError(null);
    try {
      const newPost = await createPost(postData);
      setPosts((prevPosts) => [...prevPosts, newPost]);
      return newPost;
    } catch (error) {
      handleError(error);
      throw error; // Hata durumunda hata fırlatıyoruz
    } finally {
      setLoading(false);
    }
  }, []);

  // Mevcut bir görevi ID ile güncelle
  const editPost = useCallback(async (id, postData) => {
    setLoading(true);
    setError(null);
    try {
      const updatedPost = await updatePost(id, postData);
      setPosts((prevPosts) =>
        prevPosts.map((post) => (post.id === id ? updatedPost : post))
      );
      return updatedPost;
    } catch (error) {
      handleError(error);
      throw error; // Hata durumunda hata fırlatıyoruz
    } finally {
      setLoading(false);
    }
  }, []);

  // Mevcut bir görevi ID ile sil
  const deleteExistingPost = useCallback(async (id) => {
    setLoading(true);
    setError(null);
    try {
      await deletePost(id);
      setPosts((prevPosts) => prevPosts.filter((post) => post.id !== id));
    } catch (error) {
      handleError(error);
      throw error; // Hata durumunda hata fırlatıyoruz
    } finally {
      setLoading(false);
    }
  }, []);

  // Component mount olduğunda tüm postları getir
  useEffect(() => {
    fetchPosts();
  }, [fetchPosts]);

  return {
    posts,
    post,
    loading,
    error,
    fetchPosts,
    fetchPost,
    addPost,
    editPost,
    deleteExistingPost,
  };
};

export default useCrmBlog;
