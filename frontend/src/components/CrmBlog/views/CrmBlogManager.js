// frontend/src/components/CrmBlog/views/CrmBlogManager.js
import React, { useState } from 'react';
import CrmBlogList from './CrmBlogList';
import CrmBlogForm from './CrmBlogForm';
import '../css/CrmBlogManager.css';

const CrmBlogManager = () => {
  const [editingPostId, setEditingPostId] = useState(null);
  const [showForm, setShowForm] = useState(false);

  const handleEdit = (postId) => {
    setEditingPostId(postId);
    setShowForm(true);
  };

  const handleFormClose = () => {
    setEditingPostId(null);
    setShowForm(false);
  };

  const handleSaveSuccess = () => {
    setShowForm(false);
    setEditingPostId(null);
  };

  const handleNewTask = () => {
    setEditingPostId(null);
    setShowForm(true);
  };

  return (
    <div className="crm-blog-manager">
      <div className="crm-blog-manager__content">
        {showForm ? (
          <div className="crm-blog-manager__form">
            <CrmBlogForm
              postId={editingPostId}
              onSaveSuccess={handleSaveSuccess}
            />
            <button
              className="crm-blog-manager__button"
              onClick={handleFormClose}
            >
              İptal
            </button>
          </div>
        ) : (
          <div className="crm-blog-manager__list">
            <CrmBlogList onEdit={handleEdit} onNewTask={handleNewTask} />
          </div>
        )}
      </div>
    </div>
  );
};

export default CrmBlogManager;
