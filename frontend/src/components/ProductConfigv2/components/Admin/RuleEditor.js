// frontend/src/components/ProductConfigv2/components/Admin/RuleEditor.js

import React, { useState } from 'react';
import configApi from '../../api/configApi';
import '../../styles/RuleEditor.css';

/**
 * RuleEditor bileşeni, admin panelinde yeni kural oluşturma ve mevcut kuralları düzenleme işlevini sağlar.
 * Bu bileşen; kural tipi, koşullar ve opsiyonel mesajı alır, ardından backend'e POST isteği göndererek kuralı kaydeder.
 *
 * Modern React 2025 standartlarına uygun olarak, fonksiyonel bileşen ve hook'lar kullanılarak, 
 * form validasyonu, hata yönetimi ve kullanıcı geri bildirimi sağlanmıştır.
 */
const RuleEditor = () => {
  // Başlangıçta kural tipi "deny" olarak ayarlanır.
  const [ruleType, setRuleType] = useState('deny');
  // Koşullar, her biri { feature, value } şeklinde nesneler içeren bir dizi olarak tutulur.
  const [conditions, setConditions] = useState([{ feature: '', value: '' }]);
  // Kural mesajı (opsiyonel)
  const [message, setMessage] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(false);

  // Yeni bir koşul eklemek için
  const handleAddCondition = () => {
    setConditions([...conditions, { feature: '', value: '' }]);
  };

  // Belirli bir koşulun güncellenmesi
  const handleConditionChange = (index, field, value) => {
    const updatedConditions = conditions.map((cond, idx) =>
      idx === index ? { ...cond, [field]: value } : cond
    );
    setConditions(updatedConditions);
  };

  // Bir koşulu kaldırmak için
  const handleRemoveCondition = (index) => {
    const updatedConditions = conditions.filter((_, idx) => idx !== index);
    setConditions(updatedConditions);
  };

  // Form gönderiminde kural verilerini oluşturur ve backend'e gönderir
  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setSuccess(false);

    // Koşulları, backend'in beklediği formatta bir nesneye dönüştürür (ör: { "featureId": "optionId", ... })
    const conditionsObj = conditions.reduce((acc, cond) => {
      if (cond.feature && cond.value) {
        acc[cond.feature] = cond.value;
      }
      return acc;
    }, {});

    const ruleData = {
      rule_type: ruleType,
      conditions: conditionsObj,
      message,
      actions: {} // Şimdilik boş; gelecekte "set" gibi kural tipleri için genişletilebilir.
    };

    try {
      // configApi üzerinden kural oluşturma isteği gönderilir.
      // configApi.createRule fonksiyonunun tanımlı olduğunu varsayıyoruz.
      await configApi.createRule(ruleData);
      setSuccess(true);
      // Formu sıfırla
      setRuleType('deny');
      setConditions([{ feature: '', value: '' }]);
      setMessage('');
    } catch (err) {
      setError(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="rule-editor">
      <h2>Kural Düzenleme</h2>
      {error && <div className="rule-editor__error">Hata: {error.message}</div>}
      {success && <div className="rule-editor__success">Kural başarıyla kaydedildi.</div>}
      <form onSubmit={handleSubmit} className="rule-editor__form">
        <div className="form-group">
          <label htmlFor="ruleType">Kural Tipi</label>
          <select
            id="ruleType"
            value={ruleType}
            onChange={(e) => setRuleType(e.target.value)}
          >
            <option value="deny">Kombinasyonu Engelle (deny)</option>
            <option value="allow">Kombinasyona İzin Ver (allow)</option>
            <option value="set">Değer Ata (set)</option>
          </select>
        </div>
        <div className="form-group">
          <label>Koşullar</label>
          {conditions.map((cond, index) => (
            <div key={index} className="condition-group">
              <input
                type="text"
                placeholder="Özellik ID"
                value={cond.feature}
                onChange={(e) => handleConditionChange(index, 'feature', e.target.value)}
                required
              />
              <input
                type="text"
                placeholder="Seçenek ID"
                value={cond.value}
                onChange={(e) => handleConditionChange(index, 'value', e.target.value)}
                required
              />
              {conditions.length > 1 && (
                <button
                  type="button"
                  className="condition-group__remove"
                  onClick={() => handleRemoveCondition(index)}
                >
                  Sil
                </button>
              )}
            </div>
          ))}
          <button
            type="button"
            className="rule-editor__add-condition"
            onClick={handleAddCondition}
          >
            Koşul Ekle
          </button>
        </div>
        <div className="form-group">
          <label htmlFor="ruleMessage">Kural Mesajı</label>
          <input
            type="text"
            id="ruleMessage"
            placeholder="Hata mesajı (opsiyonel)"
            value={message}
            onChange={(e) => setMessage(e.target.value)}
          />
        </div>
        <button type="submit" className="rule-editor__submit" disabled={loading}>
          {loading ? 'Kaydediliyor...' : 'Kuralı Kaydet'}
        </button>
      </form>
    </div>
  );
};

export default RuleEditor;
