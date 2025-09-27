// frontend/src/components/BomCostManager/utils/getMaxPositiveLevel.js

/**
 * BOM bileşenleri arasındaki en büyük pozitif level değerini döndürür.
 * Eğer pozitif level yoksa 0 döndürür.
 *
 * @param {Array} bomComponents - BOM bileşen dizisi
 * @returns {number} - En büyük pozitif level veya 0
 */
export function getMaxPositiveLevel(bomComponents = []) {
    // Tüm level değerlerini sayısal olarak alıp pozitif olanları filtrele
    const positiveLevels = bomComponents
      .map(item => Number(item.level))
      .filter(level => level > 0);
  
    if (positiveLevels.length === 0) {
      // Eğer pozitif level yoksa 0 dön
      return 0;
    }
    // En büyük pozitif level
    return Math.max(...positiveLevels);
  }
  