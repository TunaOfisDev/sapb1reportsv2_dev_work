// path: frontend/src/components/NexusCore/contexts/NotificationContext.js

// ### DÜZELTME: Import syntax'ı doğru hale getirildi ###
import React, { createContext, useState, useCallback } from 'react';
import { v4 as uuidv4 } from 'uuid';
import NotificationHost from '../components/common/Notification/NotificationHost';

export const NotificationContext = createContext(undefined);

export const NotificationProvider = ({ children }) => {
  const [notifications, setNotifications] = useState([]);

  const removeNotification = useCallback((id) => {
    setNotifications((prev) => prev.filter((n) => n.id !== id));
  }, []);

  const addNotification = useCallback((message, type = 'success', duration = 5000) => {
    const id = uuidv4();
    const newNotification = { id, message, type, duration };
    
    setNotifications((prev) => [...prev, newNotification]);

    const timer = setTimeout(() => {
      removeNotification(id);
    }, duration);

    return () => clearTimeout(timer);
  }, [removeNotification]);

  return (
    <NotificationContext.Provider value={{ addNotification }}>
      {children}
      <NotificationHost notifications={notifications} onClose={removeNotification} />
    </NotificationContext.Provider>
  );
};