/* path: frontend/src/components/NexusCore/components/common/Button/Button.jsx */

import React from 'react';
import PropTypes from 'prop-types';
import styles from './Button.module.scss'; /* .scss uzantılı stil dosyamızı import ediyoruz */

/**
 * Proje genelinde kullanılacak standart Button bileşeni.
 */
const Button = ({
  children,
  onClick,
  variant = 'primary',
  IconComponent,
  disabled = false,
  className = '',
  type = 'button',
  ...props /* Diğer tüm standart buton özellikleri (aria-label vb.) */
}) => {
  /* BEM modifier sınıfını gelen 'variant' prop'una göre dinamik olarak belirliyoruz. */
  const variantClass = styles[`button--${variant}`] || styles['button--primary'];
  const disabledClass = disabled ? styles['button--disabled'] : '';

  /* Tüm CSS sınıflarını birleştiriyoruz. */
  const buttonClasses = `${styles.button} ${variantClass} ${disabledClass} ${className}`.trim();

  return (
    <button
      type={type}
      className={buttonClasses}
      onClick={onClick}
      disabled={disabled}
      {...props}
    >
      {IconComponent && (
        <span className={styles.button__icon}>
          <IconComponent size={18} strokeWidth={2} />
        </span>
      )}
      {children}
    </button>
  );
};

/* Bileşenin alacağı prop'ların tiplerini ve gerekliliklerini tanımlamak,
   kodun kalitesini ve okunabilirliğini artıran en iyi pratiklerdendir. */
Button.propTypes = {
  children: PropTypes.node.isRequired,
  onClick: PropTypes.func,
  variant: PropTypes.oneOf(['primary', 'secondary', 'danger']),
  IconComponent: PropTypes.elementType,
  disabled: PropTypes.bool,
  className: PropTypes.string,
  type: PropTypes.oneOf(['button', 'submit', 'reset']),
};

export default Button;