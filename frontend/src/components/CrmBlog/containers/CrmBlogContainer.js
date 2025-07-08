// frontend/src/components/CrmBlog/containers/CrmBlogContainer.js
import React from 'react';
import CrmBlogManager from '../views/CrmBlogManager';
import '../css/CrmBlogContainer.css';
import useCrmBlog from '../hooks/useCrmBlog'; // Custom hook'u import ediyoruz

const CrmBlogContainer = () => {
  const { posts, error, loading } = useCrmBlog(); // Hook'tan hata ve yükleme durumlarını alıyoruz

  return (
    <div className="crm-blog-container__content">
      {loading && <p>Yükleniyor...</p>}
      {error && <p className="error-message">{error}</p>} {/* Hata mesajını ekranda gösteriyoruz */}
      {!loading && !error && <CrmBlogManager posts={posts} />}
    </div>
  );
};

export default CrmBlogContainer;

