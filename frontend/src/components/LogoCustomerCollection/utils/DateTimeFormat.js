// frontend/src/components/LogoCustomerCollection/utils/DateTimeFormat.js
const parseDateTime = (dateTimeStr) => {
  if (!dateTimeStr || typeof dateTimeStr !== 'string') return null;

  try {
    const parsed = new Date(dateTimeStr);
    return isNaN(parsed) ? null : parsed;
  } catch {
    return null;
  }
};

const formatDateTime = (dateTimeStr, locale = 'tr-TR') => {
  const date = parseDateTime(dateTimeStr);
  if (!date) return 'Tarih bilinmiyor';

  // Türkiye saatine göre formatla
  return `${date.toLocaleDateString(locale, {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
  })} ${date.toLocaleTimeString(locale, {
    hour: '2-digit',
    minute: '2-digit',
    hour12: false,
  })}`;
};

export { parseDateTime, formatDateTime };

