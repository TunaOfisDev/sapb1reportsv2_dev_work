// frontend/src/components/LogoSupplierReceivablesAging/utils/DateTimeFormat.js
const parseDateTime = (dateTimeStr) => {
  if (!dateTimeStr) {
    return null;
  }

  // ISO 8601 formatını kontrol et (örn: 2025-05-15T07:00:44.334869Z)
  if (dateTimeStr.includes('T')) {
    return new Date(dateTimeStr);
  }

  // Mevcut DD.MM.YYYY HH:mm formatı
  const [date, time] = dateTimeStr.split(' ');
  const [day, month, year] = date.split('.');
  const [hour, minute] = time.split(':');

  return new Date(year, month - 1, day, hour, minute);
};

const formatDateTime = (dateTimeStr, locale = 'tr-TR') => {
  if (!dateTimeStr) {
    return 'Tarih bilinmiyor';
  }

  const date = parseDateTime(dateTimeStr);
  if (!date || isNaN(date)) {
    return 'Geçersiz tarih';
  }

  // Saati ve dakikayı formatlayıp döndürür, saniyeyi dahil etmez
  const formattedDate = date.toLocaleDateString(locale, {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
  });
  const formattedTime = date.toLocaleTimeString(locale, {
    hour: '2-digit',
    minute: '2-digit',
  });

  return `${formattedDate} ${formattedTime}`;
};

export { parseDateTime, formatDateTime };
  
  
    