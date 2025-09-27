// frontend/src/components/GirsbergerOrdrOpqt/utils/DateTimeFormat.js

/**
 * Tarih ve saat formatını 'YYYY-MM-DDTHH:MM:SS.SSSZ' formatından 'DD.MM.YYYY HH:MM' formatına dönüştürür.
 * @param {string} dateTimeStr - Dönüştürülecek tarih ve saat stringi.
 * @returns {string} Dönüştürülmüş tarih ve saat.
 */
const formatDateTime = (dateTimeStr) => {
  if (!dateTimeStr) return ''; // Eğer tarih ve saat boş veya tanımsız ise boş string dön.
  
  const date = new Date(dateTimeStr);
  const day = String(date.getDate()).padStart(2, '0');
  const month = String(date.getMonth() + 1).padStart(2, '0'); // Ay 0-11 aralığında olduğu için +1 ekliyoruz
  const year = date.getFullYear();
  const hours = String(date.getHours()).padStart(2, '0');
  const minutes = String(date.getMinutes()).padStart(2, '0');

  return `${day}.${month}.${year} ${hours}:${minutes}`;
};

export default formatDateTime;
