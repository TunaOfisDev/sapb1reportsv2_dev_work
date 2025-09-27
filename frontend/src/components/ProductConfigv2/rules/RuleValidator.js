// frontend/src/components/ProductConfigv2/rules/RuleValidator.js

/**
 * RuleValidator.js
 *
 * Bu dosya, ürün konfigüratöründe kullanılan kuralların doğrulanmasını sağlar.
 * Özellikle "deny" tipi kuralların, kullanıcı seçimleriyle uyumunu kontrol eder.
 *
 * Kural nesnesi örneği:
 * {
 *   id: 1,
 *   rule_type: 'deny', // Şu anda yalnızca "deny" tipi kural kontrolü uygulanmaktadır.
 *   conditions: { "15": 163, "16": 188 }, // featureId: optionId eşleşmeleri
 *   message: 'Seçtiğiniz kombinasyon geçersiz!'
 * }
 *
 * Kullanıcı seçimleri nesnesi örneği:
 * {
 *   "15": 163,
 *   "16": 188,
 *   "17": 214
 * }
 */

/**
 * Belirtilen kuralın, verilen seçimler ile uyumunu kontrol eder.
 * Eğer "deny" tipi kuralın tüm koşulları sağlanıyorsa, kural ihlali gerçekleşmiş sayılır.
 *
 * @param {Object} rule - Kural nesnesi.
 * @param {Object} selections - Kullanıcı seçimlerini içeren nesne (ör. { featureId: optionId, ... }).
 * @returns {Object} - { valid: boolean, feedback: string }
 *                     Eğer kural koşulları sağlanıyorsa, valid false ve feedback kural mesajı döner.
 */
export const validateRule = (rule, selections) => {
    let valid = true;
    let feedback = '';
  
    // Şu anda yalnızca "deny" tipi kurallar kontrol ediliyor.
    if (rule.rule_type === 'deny' && rule.conditions) {
      // Kural koşullarındaki tüm featureId'lerin, selections nesnesinde eşleşip eşleşmediğini kontrol et.
      const conditionKeys = Object.keys(rule.conditions);
      const ruleMatches = conditionKeys.every(featureId => {
        return selections[featureId] === rule.conditions[featureId];
      });
  
      if (ruleMatches) {
        valid = false;
        feedback = rule.message || 'Seçtiğiniz kombinasyon geçersiz!';
      }
    }
  
    // Gelecekte "allow" veya "set" gibi kural tipleri için ek mantık eklenebilir.
    return { valid, feedback };
  };
  
  /**
   * Bir dizi kuralı, verilen seçimler üzerinde değerlendirir.
   * İlk ihlal eden kural bulunduğunda, sonuç döndürülür.
   *
   * @param {Array} rules - Kural nesneleri dizisi.
   * @param {Object} selections - Kullanıcı seçimlerini içeren nesne.
   * @returns {Object} - { valid: boolean, feedback: string }
   *                     Eğer herhangi bir kural ihlali varsa, valid false ve ilgili feedback döner.
   */
  export const validateRules = (rules, selections) => {
    for (const rule of rules) {
      const result = validateRule(rule, selections);
      if (!result.valid) {
        return result;
      }
    }
    return { valid: true, feedback: '' };
  };
  
  export default {
    validateRule,
    validateRules,
  };
  