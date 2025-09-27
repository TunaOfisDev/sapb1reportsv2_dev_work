// frontend/src/components/BomCostManager/utils/formatDate.js

/**
 * Tarih formatlama fonksiyonu.
 * @param {string | Date} date - Formatlanacak tarih.
 * @param {string} format - İstenilen tarih formatı ("DD.MM.YYYY", "YYYY-MM-DD" vb.).
 * @returns {string} Formatlanmış tarih.
 */
export function formatDate(date, format = "DD.MM.YYYY") {
  if (!date) return "-";
  
  const dateObj = typeof date === "string" ? new Date(date) : date;
  if (isNaN(dateObj.getTime())) return "Geçersiz Tarih";
  
  const day = String(dateObj.getDate()).padStart(2, "0");
  const month = String(dateObj.getMonth() + 1).padStart(2, "0");
  const year = dateObj.getFullYear();
  
  switch (format) {
      case "DD.MM.YYYY":
          return `${day}.${month}.${year}`;
      case "YYYY-MM-DD":
          return `${year}-${month}-${day}`;
      case "MM/DD/YYYY":
          return `${month}/${day}/${year}`;
      case "YYYY/MM/DD":
          return `${year}/${month}/${day}`;
      default:
          return `${day}.${month}.${year}`;
  }
}

/**
* ISO 8601 formatına uygun tarih ve saat döndürür.
* @param {string | Date} date - Formatlanacak tarih.
* @returns {string} ISO formatında tarih.
*/
export function formatToISO(date) {
  if (!date) return "";
  const dateObj = typeof date === "string" ? new Date(date) : date;
  return dateObj.toISOString();
}
