// frontend/src/components/ProductConfig/common/PCInput.js
import React, { useState } from 'react';
import PropTypes from 'prop-types';
import '../css/PCInput.css';

const PCInput = ({
    type = 'text',
    label,
    name,
    value,
    onChange,
    onBlur,
    onFocus,
    placeholder,
    error,
    helperText,
    disabled = false,
    required = false,
    className = '',
    variant = 'outlined',
    size = 'medium',
    fullWidth = false,
    startAdornment,
    endAdornment,
    multiline = false,
    rows = 3,
    maxLength,
    pattern,
    autoComplete = 'off',
    ...props
}) => {
    const [isFocused, setIsFocused] = useState(false);
    const inputId = `pc-input-${name}`;
    
    const handleFocus = (event) => {
        setIsFocused(true);
        if (onFocus) onFocus(event);
    };

    const handleBlur = (event) => {
        setIsFocused(false);
        if (onBlur) onBlur(event);
    };

    const inputClasses = `
        pc-input__field
        pc-input__field--${variant}
        pc-input__field--${size}
        ${error ? 'pc-input__field--error' : ''}
        ${isFocused ? 'pc-input__field--focused' : ''}
        ${fullWidth ? 'pc-input__field--full-width' : ''}
        ${className}
    `.trim();

    const InputComponent = multiline ? 'textarea' : 'input';

    return (
        <div className={`pc-input ${fullWidth ? 'pc-input--full-width' : ''}`}>
            {label && (
                <label htmlFor={inputId} className="pc-input__label">
                    {label}
                    {required && <span className="pc-input__required">*</span>}
                </label>
            )}
            <div className="pc-input__wrapper">
                {startAdornment && (
                    <div className="pc-input__adornment pc-input__adornment--start">
                        {startAdornment}
                    </div>
                )}
                <InputComponent
                    id={inputId}
                    type={type}
                    name={name}
                    value={value}
                    onChange={onChange}
                    onFocus={handleFocus}
                    onBlur={handleBlur}
                    placeholder={placeholder}
                    disabled={disabled}
                    required={required}
                    className={inputClasses}
                    rows={multiline ? rows : undefined}
                    maxLength={maxLength}
                    pattern={pattern}
                    autoComplete={autoComplete}
                    {...props}
                />
                {endAdornment && (
                    <div className="pc-input__adornment pc-input__adornment--end">
                        {endAdornment}
                    </div>
                )}
            </div>
            {helperText && <p className="pc-input__helper-text">{helperText}</p>}
            {error && <p className="pc-input__error-message">{error}</p>}
        </div>
    );
};

PCInput.propTypes = {
    type: PropTypes.string,
    label: PropTypes.string,
    name: PropTypes.string.isRequired,
    value: PropTypes.string.isRequired,
    onChange: PropTypes.func.isRequired,
    onBlur: PropTypes.func,
    onFocus: PropTypes.func,
    placeholder: PropTypes.string,
    error: PropTypes.string,
    helperText: PropTypes.string,
    disabled: PropTypes.bool,
    required: PropTypes.bool,
    className: PropTypes.string,
    variant: PropTypes.oneOf(['standard', 'outlined', 'filled']),
    size: PropTypes.oneOf(['small', 'medium', 'large']),
    fullWidth: PropTypes.bool,
    startAdornment: PropTypes.node,
    endAdornment: PropTypes.node,
    multiline: PropTypes.bool,
    rows: PropTypes.number,
    maxLength: PropTypes.number,
    pattern: PropTypes.string,
    autoComplete: PropTypes.string
};

export default PCInput;