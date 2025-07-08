// frontend/src/components/DynamicReport/utils/ToastNotifications.js
import React, { useState } from 'react';

// Özel hook oluştur
export const useToastNotifications = () => {
  const [notifications, setNotifications] = useState([]);

  const addNotification = (message, type) => {
    const newNotification = {
      message,
      type,
      id: Date.now(),
    };
    setNotifications([...notifications, newNotification]);
  };

  const closeNotification = (id) => {
    const updatedNotifications = notifications.filter((notification) => notification.id !== id);
    setNotifications(updatedNotifications);
  };

  return {
    notifications,
    addNotification,
    closeNotification
  };
};

const ToastNotifications = () => {
  const { notifications, closeNotification } = useToastNotifications();  // addNotification silindi

  return (
    <div className="toast-notifications">
      {notifications.map((notification) => (
        <div key={notification.id} className={`alert alert-${notification.type} alert-dismissible fade show`} role="alert">
          {notification.message}
          <button
            type="button"
            className="close"
            data-dismiss="alert"
            aria-label="Kapat"
            onClick={() => closeNotification(notification.id)}
          >
            <span aria-hidden="true">&times;</span>
          </button>
        </div>
      ))}
    </div>
  );
};

export default ToastNotifications;
