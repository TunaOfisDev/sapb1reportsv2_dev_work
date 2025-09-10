// path: frontend/src/components/NexusCore/utils/formatters.js

import { format, formatDistanceToNow } from 'date-fns';
import { tr } from 'date-fns/locale';
import popularDBList from './populardblist';

// ====================================================================
// YENİ: MERKEZİ VERİ TİPİ FORMATLAMA MEKANİZMASI
// ====================================================================

// Performans için formatlayıcıları bir kez oluşturup tekrar kullanıyoruz.
// Bu, her render'da yeni nesne oluşturulmasını engeller.

const decimalFormatter = new Intl.NumberFormat('tr-TR', {
  style: 'decimal',
  minimumFractionDigits: 2,
  maximumFractionDigits: 2,
});

const integerFormatter = new Intl.NumberFormat('tr-TR', {
  maximumFractionDigits: 0,
});

const dateTimeFormatter = new Intl.DateTimeFormat('tr-TR', {
  year: 'numeric',
  month: '2-digit',
  day: '2-digit',
  hour: '2-digit',
  minute: '2-digit',
});

const dateFormatter = new Intl.DateTimeFormat('tr-TR', {
  year: 'numeric',
  month: '2-digit',
  day: '2-digit',
});

/**
 * Gelen değeri, belirtilen veri tipine (dataType) göre formatlayan ana "tercüman" fonksiyon.
 * ReportViewer'daki akıllı tablo bu fonksiyonu kullanacak.
 * @param {any} value - Formatlanacak ham değer.
 * @param {string} dataType - API'den gelen standart tip ('decimal', 'integer', 'datetime' vb.)
 * @returns {string} - Kullanıcıya gösterilecek formatlanmış string.
 */
export const formatCell = (value, dataType) => {
  if (value === null || value === undefined) {
    return '';
  }

  switch (dataType) {
    case 'integer':
      const intValue = Number(value);
      if (isNaN(intValue)) return value;
      return integerFormatter.format(intValue);
    
    case 'decimal':
    case 'number':
      const numericValue = Number(value);
      if (isNaN(numericValue)) return value;
      return decimalFormatter.format(numericValue);
    
    case 'datetime':
      try {
        return dateTimeFormatter.format(new Date(value));
      } catch (e) {
        return String(value);
      }

    case 'date':
      try {
        return dateFormatter.format(new Date(value));
      } catch (e) {
        return String(value);
      }

    case 'boolean':
      return value ? 'Evet' : 'Hayır';
      
    case 'string':
    case 'other':
    default:
      return String(value);
  }
};


// ====================================================================
// MEVCUT YARDIMCI FONKSİYONLAR (DEĞİŞTİRİLMEDİ)
// Bu fonksiyonlar projenin başka yerlerinde kullanılıyor olabilir,
// bu yüzden güvenli bir şekilde yerlerinde bırakıyoruz.
// ====================================================================

/**
 * ISO 8601 formatındaki bir tarih metnini, Türkiye lokaline uygun,
 * okunabilir bir formata çevirir.
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
 * Bir sayıyı, Türkiye'ye özgü binlik ayraçları (.) ve ondalık ayraçları (,) ile formatlar.
 */
export const formatDynamicNumber = (value, decimalPlaces = 2) => {
    if (typeof value !== 'number' || isNaN(value)) {
        return '';
    }
    return new Intl.NumberFormat('tr-TR', {
        style: 'decimal',
        useGrouping: true,
        minimumFractionDigits: decimalPlaces,
        maximumFractionDigits: decimalPlaces,
    }).format(value);
};

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

export const truncateText = (text, maxLength = 100) => {
  if (!text || text.length <= maxLength) {
    return text;
  }
  return `${text.substring(0, maxLength)}...`;
};

export const formatNumber = (number) => {
    if (typeof number !== 'number') {
        return '';
    }
    return new Intl.NumberFormat('tr-TR').format(number);
};

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