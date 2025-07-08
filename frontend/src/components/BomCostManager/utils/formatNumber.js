// frontend/src/components/BomCostManager/utils/formatNumber.js
/**
 * Sayıları belirli bir formatta göstermek için yardımcı fonksiyon.
 * Örneğin: 1234567.89 -> "1.234.567,89"
 *
 * @param {number|string} value - Formatlanacak sayı
 * @param {number} decimals - Ondalık basamak sayısı (varsayılan: 2)
 * @returns {string} - Formatlanmış sayı
 */
export function formatNumber(value, decimals = 2) {
    if (value === null || value === undefined || isNaN(value)) return "0";

    return new Intl.NumberFormat('tr-TR', {
        minimumFractionDigits: decimals,
        maximumFractionDigits: decimals
    }).format(value);
}
