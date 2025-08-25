// path: frontend/src/components/NexusCore/components/layout/PageWrapper/PageWrapper.jsx
import React from 'react';
import PropTypes from 'prop-types';
import styles from './PageWrapper.module.scss';

/**
 * Uygulama içeriğini saran ana bileşen.
 * Sayfalara tutarlı bir dolgu (padding) ve maksimum genişlik sağlar.
 */
const PageWrapper = ({ children }) => {
  return (
    <main className={styles.pageWrapper}>
      {children}
    </main>
  );
};

PageWrapper.propTypes = {
  /** Sarmalanacak olan React bileşenleri veya JSX elementleri. */
  children: PropTypes.node.isRequired,
};

export default PageWrapper;