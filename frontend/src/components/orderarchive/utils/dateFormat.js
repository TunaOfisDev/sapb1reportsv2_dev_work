// frontend/src/components/orderarchive/utils/dateFormat.js

/**
 * Tarih formatlama fonksiyonu
 * @param {string | Date} date - Tarih değeri (string veya Date nesnesi)
 * @returns {string} - DD.MM.YYYY formatında tarih
 */
export const formatDate = (date) => {
    if (!date) return '';

    const dateObj = typeof date === 'string' ? new Date(date) : date;
    if (isNaN(dateObj.getTime())) return ''; // Geçersiz tarih kontrolü

    const day = String(dateObj.getDate()).padStart(2, '0');
    const month = String(dateObj.getMonth() + 1).padStart(2, '0'); // Aylar 0 tabanlıdır
    const year = dateObj.getFullYear();

    return `${day}.${month}.${year}`;
};
