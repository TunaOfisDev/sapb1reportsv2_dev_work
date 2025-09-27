// frontend/src/components/ProductConfigv2/utils/toUpperCaseTurkish.js

/**
 * Verilen bir metni, Türkçe karakterleri (i, ı, ş, ğ, ü, ö, ç) doğru bir şekilde
 * işleyerek tamamını büyük harfe çevirir.
 * * Standart toUpperCase() 'i' harfini 'I' olarak çevirirken,
 * bu fonksiyon 'İ' olarak doğru şekilde çevirir.
 * * @param {string} str - Büyük harfe çevrilecek metin.
 * @returns {string} - Tamamı büyük harfe çevrilmiş Türkçe metin.
 */
const toUpperCaseTurkish = (str) => {
  // Girdi null, undefined veya boş bir string değilse işlem yap
  if (!str) {
    return '';
  }
  
  // 'tr-TR' yerel ayarını kullanarak büyük harfe çevir
  return str.toLocaleUpperCase('tr-TR');
};

export default toUpperCaseTurkish;