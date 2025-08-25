// path: frontend/src/components/NexusCore/components/common/Spinner/Spinner.jsx
import React from 'react';
import PropTypes from 'prop-types';
import styles from './Spinner.module.scss';

/**
 * Proje genelinde API istekleri veya uzun süren işlemler sırasında
 * gösterilecek olan, CSS tabanlı yükleniyor animasyonu bileşeni.
 */
const Spinner = ({ size = 'md', className = '', ...props }) => {
  const containerClasses = `${styles.spinnerContainer} ${className}`.trim();

  // Boyutlandırma için BEM-tarzı bir modifier sınıfı kullanıyoruz.
  const spinnerSizeClass = styles[`spinner--${size}`];

  return (
    <div className={containerClasses} {...props}>
      <div className={`${styles.spinner} ${spinnerSizeClass}`}></div>
    </div>
  );
};

Spinner.propTypes = {
  /** Spinner boyutunu belirler: 'sm', 'md', veya 'lg'. */
  size: PropTypes.oneOf(['sm', 'md', 'lg']),
  /** Ekstra CSS sınıfları için kullanılır. */
  className: PropTypes.string,
};

export default Spinner;