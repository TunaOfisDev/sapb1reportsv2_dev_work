/* path: frontend/src/components/NexusCore/hooks/useNotifications.js */

import { useContext } from 'react';
import { NotificationContext } from '../contexts/NotificationContext';

/**
 * NotificationContext'e kolay bir erişim sağlar.
 * Bu hook, bir bileşenin global bildirimler göndermesini sağlar.
 * @returns {{addNotification: (message: string, type: 'success' | 'error') => void}}
 */
export const useNotifications = () => {
  // useContext ile anons sistemine (context'e) bağlanıyoruz.
  const context = useContext(NotificationContext);

  // Bu hook'un yanlış yerde (Provider sarmalayıcısı dışında) kullanılmasını
  // engellemek için bir güvenlik kontrolü ekliyoruz. Bu, geliştirme sırasında
  // olası hataları anında fark etmemizi sağlar.
  if (context === undefined) {
    throw new Error('useNotifications must be used within a NotificationProvider');
  }

  return context;
};