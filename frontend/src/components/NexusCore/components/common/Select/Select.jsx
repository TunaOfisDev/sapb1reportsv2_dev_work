// path: frontend/src/components/NexusCore/components/common/Select/Select.jsx
import React from 'react';
import PropTypes from 'prop-types';
import { ChevronDown } from 'react-feather';
import styles from './Select.module.scss';

/**
 * Proje genelinde kullanılacak, özel stillendirilmiş Select (açılır menü) bileşeni.
 */
const Select = ({
  id,
  label,
  value,
  onChange,
  options = [],
  disabled = false,
  error = null,
  helperText = '',
  className = '',
  ...props
}) => {
  const errorClass = error ? styles['select-group--error'] : '';
  const groupClasses = `${styles['select-group']} ${errorClass} ${className}`.trim();

  return (
    <div className={groupClasses}>
      {label && <label htmlFor={id} className={styles.label}>{label}</label>}
      <div className={styles['select-wrapper']}>
        <select
          id={id}
          value={value}
          onChange={onChange}
          disabled={disabled}
          className={styles.select}
          aria-invalid={!!error}
          aria-describedby={error ? `${id}-error-text` : (helperText ? `${id}-helper-text` : undefined)}
          {...props}
        >
          {options.map((option) => (
            <option key={option.value} value={option.value} disabled={option.disabled}>
              {option.label}
            </option>
          ))}
        </select>
        <ChevronDown className={styles['arrow-icon']} size={20} />
      </div>
      {error && <p id={`${id}-error-text`} className={styles.errorText}>{error}</p>}
      {!error && helperText && <p id={`${id}-helper-text`} className={styles.helperText}>{helperText}</p>}
    </div>
  );
};

Select.propTypes = {
  id: PropTypes.string.isRequired,
  label: PropTypes.string,
  value: PropTypes.oneOfType([PropTypes.string, PropTypes.number]).isRequired,
  onChange: PropTypes.func.isRequired,
  options: PropTypes.arrayOf(
    PropTypes.shape({
      value: PropTypes.oneOfType([PropTypes.string, PropTypes.number]).isRequired,
      label: PropTypes.string.isRequired,
      disabled: PropTypes.bool,
    })
  ).isRequired,
  disabled: PropTypes.bool,
  error: PropTypes.string,
  helperText: PropTypes.string,
  className: PropTypes.string,
};

export default Select;