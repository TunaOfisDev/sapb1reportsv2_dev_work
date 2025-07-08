// frontend/src/components/SalesOfferDocSum/utils/PivotCMSTSubTotal.js
/**
 * Pivot tablolar için üst toplamları hesaplar.
 * @param {Array} data - Tablo verisi.
 * @param {Array} keys - Toplanacak anahtarlar.
 * @returns {Object} Toplamları içeren bir nesne.
 */
const calculateSubTotals = (data, keys) => {
    // Başlangıçta her bir anahtar için toplamları sıfırla
    const totals = keys.reduce((acc, key) => {
      acc[key] = 0;
      return acc;
    }, {});
  
    // Veriler üzerinde dönerek her bir anahtar için toplama ekle
    data.forEach(row => {
      keys.forEach(key => {
        totals[key] += row[key] || 0; // Eğer değer undefined ise 0 ekle
      });
    });
  
    return totals;
  };
  
  export default calculateSubTotals;
  