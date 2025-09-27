// frontend/src/components/LogoSupplierReceivablesAging/utils/ErrorMessage.js

import PropTypes from 'prop-types';

const ErrorMessage = ({ message }) => {
  return (
    <div style={{ color: 'red', margin: '20px' }}>
      <h2>Hata Oluştu</h2>
      <p>{message}</p>
    </div>
  );
};

ErrorMessage.propTypes = {
  message: PropTypes.string.isRequired,
};

export default ErrorMessage;
