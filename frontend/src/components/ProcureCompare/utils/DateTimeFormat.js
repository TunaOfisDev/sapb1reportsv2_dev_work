// File: frontend/src/components/ProcureCompare/utils/DateTimeFormat.js

const parseDateTime = (dateTimeStr) => {
  if (!dateTimeStr) return null;

  const date = new Date(dateTimeStr);
  return isNaN(date.getTime()) ? null : date;
};

const formatDate = (dateStr) => {
  const date = parseDateTime(dateStr);
  if (!date) return 'Tarih bilinmiyor';

  const pad = (n) => n.toString().padStart(2, '0');
  const day = pad(date.getDate());
  const month = pad(date.getMonth() + 1);
  const year = date.getFullYear();

  return `${day}.${month}.${year}`;
};

const formatDateTime = (dateTimeStr) => {
  const date = parseDateTime(dateTimeStr);
  if (!date) return 'Tarih bilinmiyor';

  const pad = (n) => n.toString().padStart(2, '0');
  const day = pad(date.getDate());
  const month = pad(date.getMonth() + 1);
  const year = date.getFullYear();
  const hours = pad(date.getHours());
  const minutes = pad(date.getMinutes());

  return `${day}.${month}.${year} ${hours}:${minutes}`;
};

export { parseDateTime, formatDate, formatDateTime };
