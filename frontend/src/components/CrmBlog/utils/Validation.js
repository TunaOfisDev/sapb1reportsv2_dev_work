// frontend/src/components/CrmBlog/utils/Validation.js

const validateTaskTitle = (taskTitle) => {
    if (!taskTitle || taskTitle.trim() === '') {
      return 'Görev başlığı boş olamaz';
    }
    if (taskTitle.length > 255) {
      return 'Görev başlığı 255 karakterden uzun olamaz';
    }
    return null;
  };
  
  const validateProjectName = (projectName) => {
    if (projectName.length > 255) {
      return 'Proje adı 255 karakterden uzun olamaz';
    }
    return null;
  };
  
  const validateDeadline = (deadline) => {
    if (!deadline) {
      return 'Son tarih boş olamaz';
    }
    const date = new Date(deadline);
    if (isNaN(date.getTime())) {
      return 'Geçersiz tarih formatı';
    }
    return null;
  };
  
  const validateTaskDescription = (taskDescription) => {
    // Görev açıklamaları için özel bir kural yok, boş olabilir.
    return null;
  };
  
  const validateStatus = (status) => {
    const validStatuses = [0, 1, 2]; // Taslak, Yayınla, Arşiv
    if (!validStatuses.includes(status)) {
      return 'Geçersiz durum değeri';
    }
    return null;
  };
  
  const validatePost = (post) => {
    const errors = {};
  
    const taskTitleError = validateTaskTitle(post.task_title);
    if (taskTitleError) {
      errors.task_title = taskTitleError;
    }
  
    const projectNameError = validateProjectName(post.project_name);
    if (projectNameError) {
      errors.project_name = projectNameError;
    }
  
    const deadlineError = validateDeadline(post.deadline);
    if (deadlineError) {
      errors.deadline = deadlineError;
    }
  
    const taskDescriptionError = validateTaskDescription(post.task_description);
    if (taskDescriptionError) {
      errors.task_description = taskDescriptionError;
    }
  
    const statusError = validateStatus(post.status);
    if (statusError) {
      errors.status = statusError;
    }
  
    return errors;
  };
  
  export {
    validateTaskTitle,
    validateProjectName,
    validateDeadline,
    validateTaskDescription,
    validateStatus,
    validatePost,
  };
  