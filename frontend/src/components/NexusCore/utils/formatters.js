/* path: frontend/src/components/NexusCore/utils/formatters.js */

import { format } from 'date-fns';
import { tr } from 'date-fns/locale';

/**
 * ISO 8601 formatındaki bir tarih metnini, Türkiye lokaline uygun,
 * okunabilir bir formata çevirir.
 * @param {string | Date} dateString - Formatlanacak tarih.
 * @returns {string} Örn: "25 Ağustos 2025, 15:17"
 */
export const formatDateTime = (dateString) => {
  if (!dateString) return '';
  try {
    const date = new Date(dateString);
    return format(date, 'dd MMMM yyyy, HH:mm', { locale: tr });
  } catch (error) {
    console.error("Geçersiz tarih formatı:", dateString, error);
    return 'Geçersiz Tarih';
  }
};

/**
 * Bir sanal tablonun paylaşım statüsünü, UI'da kullanılacak
 * bir bilgi paketine dönüştürür (metin, ikon, renk).
 * @param {string} status - 'PRIVATE', 'PUBLIC_READONLY', 'PUBLIC_EDITABLE'
 * @returns {{text: string, icon: string, color: string}}
 */
export const formatSharingStatus = (status) => {
  switch (status) {
    case 'PRIVATE':
      return { text: 'Özel', icon: 'lock-alt', color: 'secondary' };
    case 'PUBLIC_READONLY':
      return { text: 'Halka Açık (Salt Okunur)', icon: 'eye', color: 'info' };
    case 'PUBLIC_EDITABLE':
      return { text: 'Halka Açık (Düzenlenebilir)', icon: 'users', color: 'success' };
    default:
      return { text: 'Bilinmiyor', icon: 'alert-triangle', color: 'warning' };
  }
};

/**
 * Veri tabanı türü kodunu, okunabilir bir metne ve ikon ismine çevirir.
 * @param {string} dbType - 'POSTGRESQL', 'SQL_SERVER' vb.
 * @returns {{text: string, icon: string}}
 */
export const formatDbType = (dbType) => {
    const type = dbType.toUpperCase();
    switch (type) {
      case 'POSTGRESQL':
        return { text: 'PostgreSQL', icon: 'postgresql' };
      case 'SQL_SERVER':
        return { text: 'MS SQL Server', icon: 'sql-server' };
      case 'MYSQL':
        return { text: 'MySQL', icon: 'mysql' };
      /* Diğer DB tipleri buraya eklenebilir */
      default:
        return { text: 'Veri Tabanı', icon: 'database' };
    }
};

/**
 * Uzun bir metni, belirtilen karakter sayısına göre kısaltır ve sonuna "..." ekler.
 * @param {string} text - Kısaltılacak metin.
 * @param {number} [maxLength=100] - İzin verilen maksimum karakter sayısı.
 * @returns {string} Kısaltılmış metin.
 */
export const truncateText = (text, maxLength = 100) => {
  if (!text || text.length <= maxLength) {
    return text;
  }
  return `${text.substring(0, maxLength)}...`;
};

/**
 * Bir sayıyı, Türkiye'ye özgü binlik ayraçları (.) ile formatlar.
 * @param {number} number - Formatlanacak sayı.
 * @returns {string} Örn: 12345.67 -> "12.345,67"
 */
export const formatNumber = (number) => {
    if (typeof number !== 'number') {
        return '';
    }
    // Intl.NumberFormat, tarayıcının kendi, güçlü formatlama motorunu kullanır.
    return new Intl.NumberFormat('tr-TR').format(number);
};