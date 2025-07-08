// frontend/src/components/TunaInsSupplierPayment/hooks/SupplierPaymentUpdates.js
import React from 'react';

const SupplierPaymentUpdates = ({ messages }) => {
  return (
    <div>
      <h3>Supplier Payment Updates</h3>
      <ul>
        {messages.map((msg, index) => (
          <li key={index}>{msg}</li>
        ))}
      </ul>
    </div>
  );
};

export default SupplierPaymentUpdates;
