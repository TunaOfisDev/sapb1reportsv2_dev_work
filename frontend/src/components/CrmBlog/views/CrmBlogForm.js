// frontend/src/components/CrmBlog/views/CrmBlogForm.js
import React, { useState, useEffect } from 'react';
import useCrmBlog from '../hooks/useCrmBlog';
import {
  validateTaskTitle,
  validateProjectName,
  validateDeadline,
  validateTaskDescription,
  validateStatus,
  validatePost,
} from '../utils/Validation';
import '../css/CrmBlogForm.css';

const CrmBlogForm = ({ postId, onSaveSuccess }) => {
  const { addPost, editPost, fetchPost, post, loading, error } = useCrmBlog();
  const [formData, setFormData] = useState({
    task_title: '',
    project_name: '',
    deadline: '',
    task_description: '',
    status: 1,
  });
  const [formErrors, setFormErrors] = useState({});

  useEffect(() => {
    if (postId) {
      fetchPost(postId);
    }
  }, [postId, fetchPost]);

  useEffect(() => {
    if (post) {
      setFormData({
        task_title: post.task_title,
        project_name: post.project_name,
        deadline: post.deadline,
        task_description: post.task_description,
        status: post.status,
      });
    }
  }, [post]);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData({
      ...formData,
      [name]: value,
    });

    // Field-level validation
    let error = null;
    switch (name) {
      case 'task_title':
        error = validateTaskTitle(value);
        break;
      case 'project_name':
        error = validateProjectName(value);
        break;
      case 'deadline':
        error = validateDeadline(value);
        break;
      case 'task_description':
        error = validateTaskDescription(value);
        break;
      case 'status':
        error = validateStatus(Number(value));
        break;
      default:
        break;
    }
    setFormErrors({
      ...formErrors,
      [name]: error,
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    const errors = validatePost(formData);
    if (Object.keys(errors).length > 0) {
      setFormErrors(errors);
      return;
    }

    try {
      if (postId) {
        await editPost(postId, formData);
      } else {
        await addPost(formData);
      }
      onSaveSuccess();
    } catch (err) {
      console.error('Error saving post:', err);
    }
  };

  return (
    <form className="crm-blog-form" onSubmit={handleSubmit}>
      <div className="crm-blog-form__header">
        <h2 className="crm-blog-form__title">{postId ? 'Görev Düzenle' : 'Yeni Görev'}</h2>
      </div>
      <div className="crm-blog-form__group">
        <label className="crm-blog-form__label" htmlFor="task_title">Görev Başlığı</label>
        <input
          className="crm-blog-form__input"
          type="text"
          id="task_title"
          name="task_title"
          value={formData.task_title}
          onChange={handleChange}
        />
        {formErrors.task_title && <span className="crm-blog-form__error">{formErrors.task_title}</span>}
      </div>
      <div className="crm-blog-form__group">
        <label className="crm-blog-form__label" htmlFor="project_name">Proje Adı</label>
        <input
          className="crm-blog-form__input"
          type="text"
          id="project_name"
          name="project_name"
          value={formData.project_name}
          onChange={handleChange}
        />
        {formErrors.project_name && <span className="crm-blog-form__error">{formErrors.project_name}</span>}
      </div>
      <div className="crm-blog-form__group">
        <label className="crm-blog-form__label" htmlFor="deadline">Son Tarih</label>
        <input
          className="crm-blog-form__input"
          type="date"
          id="deadline"
          name="deadline"
          value={formData.deadline}
          onChange={handleChange}
        />
        {formErrors.deadline && <span className="crm-blog-form__error">{formErrors.deadline}</span>}
      </div>
      <div className="crm-blog-form__group">
        <label className="crm-blog-form__label" htmlFor="task_description">Görev Açıklamaları</label>
        <textarea
          className="crm-blog-form__textarea"
          id="task_description"
          name="task_description"
          value={formData.task_description}
          onChange={handleChange}
        ></textarea>
        {formErrors.task_description && <span className="crm-blog-form__error">{formErrors.task_description}</span>}
      </div>

      <div className="crm-blog-form__actions">
        <button className="crm-blog-form__button" type="submit" disabled={loading}>
          {postId ? 'Güncelle' : 'Oluştur'}
        </button>
      </div>
      {error && <div className="crm-blog-form__error">Hata: {error.message}</div>}
    </form>
  );
};

export default CrmBlogForm;
