// frontend/src/components/ProductConfigv2/utils/textUtils.js (YENİ DOSYA)

/**
 * Bir metni, Türkçe karakter duyarsız arama yapmaya uygun hale getirir.
 * Tüm harfleri küçültür ve Türkçe karakterleri ASCII karşılıklarına çevirir.
 * Örnek: "ÇANKAYA PROJESİ" -> "cankaya projesi"
 */
export const normalizeForSearch = (text) => {
  if (typeof text !== 'string') return '';
  
  return text
    .toLowerCase()
    .replace(/ı/g, 'i')
    .replace(/ş/g, 's')
    .replace(/ğ/g, 'g')
    .replace(/ü/g, 'u')
    .replace(/ö/g, 'o')
    .replace(/ç/g, 'c');
};