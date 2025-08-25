/* path: frontend/src/components/NexusCore/contexts/NotificationContext.js */

import React, { createContext, useState, useCallback, useContext } from 'react';

// Context'i dışarıdan erişilebilir hale getirmek için export ediyoruz.
export const NotificationContext = createContext(undefined);

export const NotificationProvider = ({ children }) => {
  const [notification, setNotification] = useState(null);

  const addNotification = useCallback((message, type = 'success') => {
    setNotification({ message, type });
    setTimeout(() => {
      setNotification(null);
    }, 5000);
  }, []);

  return (
    <NotificationContext.Provider value={{ addNotification }}>
      {children}
      {notification && (
        <div className={`nexus-notification ${notification.type}`}>
          {notification.message}
        </div>
      )}
    </NotificationContext.Provider>
  );
};

/* Bu hook'u artık kendi dosyasına taşıyacağımız için buradan silebiliriz,
   ancak burada kalmasının da bir zararı yoktur. Temizlik açısından kendi
   dosyasında olması daha iyidir. */
// export const useNotifications = () => {
//   return useContext(NotificationContext);
// };