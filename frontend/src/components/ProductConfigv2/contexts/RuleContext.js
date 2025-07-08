// frontend/src/components/ProductConfigv2/contexts/RuleContext.js

import React, { createContext, useContext, useState } from 'react';

/**
 * RuleContext, ürün konfigüratöründe kullanılan kurallarla ilgili global state'i yönetir.
 * Bu context sayesinde, kurallar, kural doğrulama sonucu (feedback, geçerlilik) ve hata durumları
 * merkezi bir şekilde paylaşılabilir.
 */
const RuleContext = createContext();

export const RuleProvider = ({ children }) => {
  // API'den alınan kural listesi
  const [rules, setRules] = useState([]);
  // Kurallar değerlendirilirken oluşan uyarı mesajı
  const [feedback, setFeedback] = useState('');
  // Seçimlerin kurallara göre geçerliliği
  const [isValid, setIsValid] = useState(true);
  // Hata yönetimi için state
  const [error, setError] = useState(null);

  const contextValue = {
    rules,
    setRules,
    feedback,
    setFeedback,
    isValid,
    setIsValid,
    error,
    setError,
  };

  return (
    <RuleContext.Provider value={contextValue}>
      {children}
    </RuleContext.Provider>
  );
};

/**
 * useRuleContext hook'u, RuleContext'e kolay erişim sağlar.
 * Bu hook'u, kural listesi, kural doğrulama sonucu ve hata bilgilerine erişmek için kullanabilirsin.
 */
export const useRuleContext = () => {
  const context = useContext(RuleContext);
  if (!context) {
    throw new Error('useRuleContext must be used within a RuleProvider');
  }
  return context;
};

export default RuleContext;
