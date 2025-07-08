// frontend/src/components/DeliveryDocSum/utils/DateTimeFormat.js
const parseDateTime = (dateTimeStr) => {
    if (!dateTimeStr) {
      return null;
    }
  
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
    // Saati ve dakikayı formatlayıp döndürür, saniyeyi dahil etmez
    const formattedDate = date.toLocaleDateString(locale);
    const formattedTime = date.toLocaleTimeString(locale, { hour: '2-digit', minute: '2-digit' });
  
    return `${formattedDate} ${formattedTime}`;
  };
  
  export { parseDateTime, formatDateTime };
  
  
    