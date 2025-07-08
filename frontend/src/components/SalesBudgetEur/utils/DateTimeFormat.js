// frontend/src/components/SalesBudgetEur/utils/DateTimeFormat.js
const formatDateTime = (isoDateTimeStr, locale = 'tr-TR') => {
  if (!isoDateTimeStr) {
    return 'Tarih bilinmiyor';
  }

  // ISO 8601 formatını Date objesine dönüştür
  const date = new Date(isoDateTimeStr);

  // Tarih ve saat bilgisini istenilen formata çevir
  const options = { year: 'numeric', month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit' };
  const formattedDateTime = date.toLocaleString(locale, options).replace(/(\d{2})\/(\d{2})\/(\d{4}), (\d{2}):(\d{2})/, '$3.$2.$1 $4:$5');

  return formattedDateTime;
};

export { formatDateTime };

  
  
    