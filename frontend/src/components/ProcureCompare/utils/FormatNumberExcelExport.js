// File: frontend/src/components/ProcureCompare/utils/FormatNumberExcelExport.js

/**
 * Excel dışa aktarma için sayıları sadece virgüllü ondalıkla formatlar (binlik ayraç yok).
 * Örnek: 1234567.89 => "1234567,89"
 *
 * @param {number|string} value
 * @returns {string}
 */
const formatNumberExcelExport = (value) => {
    if (isNaN(value)) return value;
  
    return Number(value).toLocaleString('tr-TR', {
      useGrouping: false, // Binlik ayraç yok
      minimumFractionDigits: 2,
      maximumFractionDigits: 2
    });
  };
  
  export default formatNumberExcelExport;
  