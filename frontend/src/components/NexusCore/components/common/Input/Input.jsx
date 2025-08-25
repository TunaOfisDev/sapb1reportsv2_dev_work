// path: frontend/src/components/NexusCore/components/common/Input/Input.jsx
import React from 'react';
import PropTypes from 'prop-types';
import styles from './Input.module.scss';

/**
 * Proje genelinde kullanılacak standart Input (girdi) bileşeni.
 * Hata durumu ve yardım metni gibi özellikler de eklenmiştir.
 */
const Input = ({
  id,
  label,
  type = 'text',
  value,
  onChange,
  placeholder,
  disabled = false,
  error = null,
  helperText = '',
  className = '',
  ...props
}) => {
  // Hata durumunda uygulanacak CSS sınıfını belirliyoruz.
  const errorClass = error ? styles['input-group--error'] : '';
  
  // Gelen ek sınıfları da birleştiriyoruz.
  const groupClasses = `${styles['input-group']} ${errorClass} ${className}`.trim();

  return (
    <div className={groupClasses}>
      {label && <label htmlFor={id} className={styles.label}>{label}</label>}
      <input
        id={id}
        type={type}
        value={value}
        onChange={onChange}
        placeholder={placeholder}
        disabled={disabled}
        className={styles.input}
        aria-invalid={!!error} // Erişilebilirlik için hata durumunu belirtir
        aria-describedby={error ? `${id}-error-text` : (helperText ? `${id}-helper-text` : undefined)}
        {...props}
      />
      {error && <p id={`${id}-error-text`} className={styles.errorText}>{error}</p>}
      {!error && helperText && <p id={`${id}-helper-text`} className={styles.helperText}>{helperText}</p>}
    </div>
  );
};

Input.propTypes = {
  id: PropTypes.string.isRequired,
  label: PropTypes.string,
  type: PropTypes.string,
  value: PropTypes.oneOfType([PropTypes.string, PropTypes.number]).isRequired,
  onChange: PropTypes.func.isRequired,
  placeholder: PropTypes.string,
  disabled: PropTypes.bool,
  error: PropTypes.string,
  helperText: PropTypes.string,
  className: PropTypes.string,
};

export default Input;