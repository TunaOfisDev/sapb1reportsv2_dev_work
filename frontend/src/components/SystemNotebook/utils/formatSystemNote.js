// frontend/src/components/SystemNotebook/utils/formatSystemNote.js

/**
 * ISO tarih formatını okunabilir hale çevirir (örnek: 2025-05-18T14:30 → 18.05.2025 14:30)
 * @param {string} isoDate - ISO 8601 tarih stringi
 * @returns {string} - Formatlanmış tarih
 */
export const formatDateTime = (isoDate) => {
  if (!isoDate) return '';
  const date = new Date(isoDate);
  return date.toLocaleString('tr-TR', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  });
};

/**
 * İçeriği belli bir karakterden sonra kısaltır
 * @param {string} content - Not içeriği
 * @param {number} maxLength - Maksimum karakter sayısı (default: 200)
 * @returns {string}
 */
export const truncateContent = (content, maxLength = 200) => {
  if (!content) return '';
  return content.length > maxLength
    ? content.substring(0, maxLength).trim() + '...'
    : content;
};

/**
 * Kaynak bilgisini simgeye çevirir (badge gibi kullanım için)
 * @param {string} source - 'github' | 'admin'
 * @returns {string}
 */
export const formatSourceLabel = (source) => {
  switch (source) {
    case 'github':
      return 'GitHub';
    case 'admin':
      return 'SystemAdmin';
    default:
      return 'Bilinmiyor';
  }
};
