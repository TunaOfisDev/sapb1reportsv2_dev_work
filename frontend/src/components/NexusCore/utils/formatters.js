// path: frontend/src/components/NexusCore/utils/formatters.js

import { format, formatDistanceToNow } from 'date-fns';
import { tr } from 'date-fns/locale';
import popularDBList from './populardblist';

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
      return { text: 'Özel', icon: 'lock', color: 'secondary' };
    case 'PUBLIC_READONLY':
      return { text: 'Salt Okunur', icon: 'eye', color: 'info' };
    case 'PUBLIC_EDITABLE':
      return { text: 'Düzenlenebilir', icon: 'users', color: 'success' };
    default:
      return { text: 'Bilinmiyor', icon: 'alert-triangle', color: 'warning' };
  }
};

/**
 * Veri tabanı türü kodunu, `populardblist`'ten arayarak
 * okunabilir bir metne ve ikon ismine çevirir.
 * @param {string} dbType - 'postgresql', 'sap_hana' vb.
 * @returns {{text: string, icon: string}}
 */
export const formatDbType = (dbType) => {
    if (!dbType) {
        return { text: 'Bilinmiyor', icon: 'help-circle' };
    }

    const dbInfo = popularDBList.find(db => db.value === dbType);

    if (dbInfo) {
        return { text: dbInfo.label, icon: dbInfo.icon };
    }

    return { text: dbType, icon: 'database' };
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
    return new Intl.NumberFormat('tr-TR').format(number);
};

// ### YENİ FONKSİYON: Oncelikli olarak bu fonksiyonu kullanacagiz ###
/**
 * Bir sayıyı ondalık hassasiyetine göre formatlar.
 * @param {number} value - Formatlanacak sayı.
 * @param {number} [decimalPlaces=2] - Gösterilecek ondalık basamak sayısı.
 * @returns {string} Örn: 12345.6789 -> "12.345,68" (2 ondalık basamak için)
 */
export const formatDynamicNumber = (value, decimalPlaces = 2) => {
  if (typeof value !== 'number' || isNaN(value)) {
      return '';
  }
  return new Intl.NumberFormat('tr-TR', {
      minimumFractionDigits: decimalPlaces,
      maximumFractionDigits: decimalPlaces,
  }).format(value);
};

/**
 * Bir tarih metnini, şu anki zamana göre "göreli" bir formata çevirir.
 * "Twitter tarzı" zaman gösterimi için.
 * @param {string | Date} dateString - Geçmişteki tarih.
 * @returns {string} Örn: "5 dakika önce", "yaklaşık 2 ay önce"
 */
export const formatRelativeTime = (dateString) => {
  if (!dateString) return '';
  try {
    const date = new Date(dateString);
    return formatDistanceToNow(date, { addSuffix: true, locale: tr });
  } catch (error) {
    console.error("Geçersiz göreli tarih formatı:", dateString, error);
    return 'Geçersiz Tarih';
  }
};