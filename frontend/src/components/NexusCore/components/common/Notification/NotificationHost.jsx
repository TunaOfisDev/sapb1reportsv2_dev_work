// path: frontend/src/components/NexusCore/components/common/Notification/NotificationHost.jsx
import React from 'react';
import PropTypes from 'prop-types';
import { CheckCircle, AlertTriangle, XCircle, Info, X } from 'react-feather';
import styles from './Notification.module.scss';

const icons = {
  success: <CheckCircle />,
  error: <XCircle />,
  warning: <AlertTriangle />,
  info: <Info />,
};

const Notification = ({ notification, onClose }) => {
  const { id, message, type } = notification;
  const icon = icons[type] || <Info />;

  return (
    <div className={`${styles.notification} ${styles[type]}`}>
      <div className={styles.icon}>{icon}</div>
      <div className={styles.message}>{message}</div>
      <button onClick={() => onClose(id)} className={styles.closeButton}>
        <X size={18} />
      </button>
    </div>
  );
};

const NotificationHost = ({ notifications, onClose }) => {
  return (
    <div className={styles.notificationHost}>
      {notifications.map((n) => (
        <Notification key={n.id} notification={n} onClose={onClose} />
      ))}
    </div>
  );
};

Notification.propTypes = {
  notification: PropTypes.object.isRequired,
  onClose: PropTypes.func.isRequired,
};

NotificationHost.propTypes = {
    notifications: PropTypes.array.isRequired,
    onClose: PropTypes.func.isRequired
}

export default NotificationHost;