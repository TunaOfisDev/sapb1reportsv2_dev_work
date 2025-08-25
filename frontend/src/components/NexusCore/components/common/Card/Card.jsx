/* path: frontend/src/components/NexusCore/components/common/Card/Card.jsx */

import React from 'react';
import PropTypes from 'prop-types';
import styles from './Card.module.scss';

const Card = ({ title, headerActions, children, footer, className = '', ...props }) => {
  const cardClasses = `${styles.card} ${className}`.trim();

  return (
    <div className={cardClasses} {...props}>
      {(title || headerActions) && (
        <header className={styles.card__header}>
          {title && <h2 className={styles.card__title}>{title}</h2>}
          {headerActions && <div className={styles.card__actions}>{headerActions}</div>}
        </header>
      )}
      <main className={styles.card__body}>
        {children}
      </main>
      {footer && (
        <footer className={styles.card__footer}>
          {footer}
        </footer>
      )}
    </div>
  );
};

Card.propTypes = {
  title: PropTypes.string,
  headerActions: PropTypes.node,
  children: PropTypes.node.isRequired,
  footer: PropTypes.node,
  className: PropTypes.string,
};

export default Card;