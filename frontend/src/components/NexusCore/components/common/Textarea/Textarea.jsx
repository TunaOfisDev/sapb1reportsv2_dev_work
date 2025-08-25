// path: frontend/src/components/NexusCore/components/common/Textarea/Textarea.jsx
import React from 'react';
import PropTypes from 'prop-types';
import styles from './Textarea.module.scss';

const Textarea = ({
  id,
  label,
  value,
  onChange,
  placeholder,
  disabled = false,
  error = null,
  helperText = '',
  className = '',
  rows = 5,
  ...props
}) => {
  const errorClass = error ? styles['textarea-group--error'] : '';
  const groupClasses = `${styles['textarea-group']} ${errorClass} ${className}`.trim();

  return (
    <div className={groupClasses}>
      {label && <label htmlFor={id} className={styles.label}>{label}</label>}
      <textarea
        id={id}
        value={value}
        onChange={onChange}
        placeholder={placeholder}
        disabled={disabled}
        className={styles.textarea}
        rows={rows}
        aria-invalid={!!error}
        aria-describedby={error ? `${id}-error-text` : (helperText ? `${id}-helper-text` : undefined)}
        {...props}
      />
      {error && <p id={`${id}-error-text`} className={styles.errorText}>{error}</p>}
      {!error && helperText && <p id={`${id}-helper-text`} className={styles.helperText}>{helperText}</p>}
    </div>
  );
};

Textarea.propTypes = {
  id: PropTypes.string.isRequired,
  label: PropTypes.string,
  value: PropTypes.string.isRequired,
  onChange: PropTypes.func.isRequired,
  placeholder: PropTypes.string,
  disabled: PropTypes.bool,
  error: PropTypes.string,
  helperText: PropTypes.string,
  className: PropTypes.string,
  rows: PropTypes.number,
};

export default Textarea;