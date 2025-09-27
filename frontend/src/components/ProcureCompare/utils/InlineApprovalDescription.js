// File: frontend/src/components/ProcureCompare/utils/InlineApprovalDescription.js

import React, { useState } from 'react';
import '../css/InlineApprovalDescription.css';

const InlineApprovalDescription = ({ onSubmit, onCancel, placeholder = "Lütfen açıklama girin..." }) => {
  const [description, setDescription] = useState('');
  const [error, setError] = useState(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [successMessage, setSuccessMessage] = useState(null);

  const handleSubmit = async () => {
    if (!description.trim()) {
      setError("Lütfen bir açıklama girin.");
      return;
    }

    try {
      setIsSubmitting(true);
      setError(null);
      await onSubmit(description);
      setSuccessMessage("✅ Açıklamanız başarıyla gönderildi.");
      setDescription('');
      setTimeout(() => {
        setSuccessMessage(null);
      }, 3000);
    } catch (err) {
      console.error('Gönderim hatası:', err);
      setError('❌ Gönderim sırasında bir hata oluştu.');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="inline-approval__wrapper">
      <textarea
        className="inline-approval__textarea"
        placeholder={placeholder}
        value={description}
        onClick={(e) => e.stopPropagation()}  // <<< EKLENECEK
        onChange={(e) => {
          setDescription(e.target.value);
          if (error) setError(null); // Kullanıcı yazınca hata mesajı kaybolsun
        }}
        disabled={isSubmitting}
      />


      {(error || successMessage) && (
        <div className={`inline-approval__message ${error ? 'error' : 'success'}`}>
          {error || successMessage}
        </div>
      )}

      <div className="inline-approval__actions">
      <button
          className="inline-approval__btn inline-approval__btn--cancel"
          onClick={(e) => {
            e.stopPropagation();  // <<< EKLENECEK
            onCancel();
          }}
          disabled={isSubmitting}
        >
          İptal
        </button>
        <button
          className="inline-approval__btn inline-approval__btn--submit"
          onClick={(e) => {
            e.stopPropagation();  // <<< EKLENECEK
            handleSubmit();
          }}
          disabled={isSubmitting}
        >
          {isSubmitting ? 'Gönderiliyor...' : 'Gönder'}
        </button>

      </div>
    </div>
  );
};

export default InlineApprovalDescription;
