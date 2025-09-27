// frontend/src/components/LogoCustomerBalance/utils/DateFormat.js

/**
 * Tarih formatını 'YYYY-MM-DD' formatından 'DD.MM.YYYY' formatına dönüştürür.
 * @param {string} dateStr - Dönüştürülecek tarih stringi.
 * @returns {string} Dönüştürülmüş tarih.
 */
const formatDate = (dateStr) => {
  if (!dateStr) return ''; // Eğer tarih boş veya tanımsız ise boş string dön.
  
  const dateParts = dateStr.split('-'); // Tarihi '-' karakterine göre böl.
  
  if (dateParts.length !== 3) return dateStr; // Eğer bölünen tarih doğru bir şekilde üç parçaya bölünmediyse, orijinal stringi dön.

  const [year, month, day] = dateParts; // Yıl, ay ve günü parçalarından çıkar.

  return `${day}.${month}.${year}`; // 'DD.MM.YYYY' formatında string dön.
};

export default formatDate;

  
    