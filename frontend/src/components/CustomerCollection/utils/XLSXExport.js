// frontend/src/components/CustomerCollection/utils/XLSXExport.js
import * as XLSX from 'xlsx';

function getUniqueMonthKeys(data) {
  const monthSet = new Set();
  data.forEach(d => {
    try {
      // Eğer monthly_balances zaten bir nesne ise veya geçerli bir JSON stringi ise
      const monthlyBalances = typeof d.monthly_balances === 'string' ? JSON.parse(d.monthly_balances) : d.monthly_balances;
      Object.keys(monthlyBalances).forEach(month => monthSet.add(month));
    } catch (error) {
      // JSON.parse hataları için log
      console.error('Error parsing monthly_balances:', error);
    }
  });
  return Array.from(monthSet).sort();
}

function convertToSheetData(data, monthKeys) {
  return data.map(d => {
    const monthlyBalances = typeof d.monthly_balances === 'string' ? JSON.parse(d.monthly_balances) : d.monthly_balances;
    const monthData = monthKeys.reduce((acc, month) => {
      acc[month] = monthlyBalances[month] || 0;
      return acc;
    }, {});
    // monthly_balances'ı döndürülen objeden çıkarıyoruz.
    const { monthly_balances, ...rest } = d;
    return { ...rest, ...monthData };
  });
}

const XLSXExport = {
  exportToExcel: (data, fileName) => {
    const monthKeys = getUniqueMonthKeys(data);
    const sheetData = convertToSheetData(data, monthKeys);
    const ws = XLSX.utils.json_to_sheet(sheetData);
    const wb = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(wb, ws, 'Tedarikçi Ödemeleri');
    XLSX.writeFile(wb, `${fileName}.xlsx`);
  }
};

export default XLSXExport;


