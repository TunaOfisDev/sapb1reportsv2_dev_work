// frontend/src/components/Activities/utils/DateFormat.js

const formatDate = (dateStr) => {
  if (!dateStr) return '';
  
  const date = new Date(dateStr);
  if (isNaN(date.getTime())) return dateStr;

  const gun = String(date.getDate()).padStart(2, '0');
  const ay  = String(date.getMonth() + 1).padStart(2, '0');
  const yil = date.getFullYear();

  return `${gun}.${ay}.${yil}`;
};

// ISO 8601 tarih-saat formatını DD.MM.YYYY HH:MM biçiminde döndürür
const formatDateTime = (isoStr) => {
  if (!isoStr) return '';
  const date = new Date(isoStr);

  if (isNaN(date.getTime())) return isoStr;

  const gun = String(date.getDate()).padStart(2, '0');
  const ay  = String(date.getMonth() + 1).padStart(2, '0');
  const yil = date.getFullYear();
  const saat = String(date.getHours()).padStart(2, '0');
  const dk   = String(date.getMinutes()).padStart(2, '0');

  return `${gun}.${ay}.${yil} ${saat}:${dk}`;
};

export { formatDate, formatDateTime };
