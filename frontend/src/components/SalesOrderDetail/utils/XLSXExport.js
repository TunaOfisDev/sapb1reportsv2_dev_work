// frontend/src/components/SalesOrderDetail/utils/XLSXExport.js
import * as XLSX from 'xlsx';

// Helper function to format numbers as "###.###,00"
function formatNumber(num) {
  return num.toLocaleString('tr-TR', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).replace(',', 'DECIMAL').replace(/\./g, ',').replace('DECIMAL', '.');
}

// Function to generate an Excel file and trigger a download
function XLSXExport(data, fileName = 'CustomerSalesData.xlsx') {
  // Convert data to worksheet
  const worksheet = XLSX.utils.json_to_sheet(data.map(d => ({
    'Müşteri Kodu': d.musteri_kod,
    'Müşteri Adı': d.musteri_ad,
    'Yıllık Toplam': formatNumber(d.yillik_toplam),
    // ... other months similarly
    'Aralık': formatNumber(d.aralik),
  })), {
    header: ['Müşteri Kodu', 'Müşteri Adı', 'Yıllık Toplam', 'Ocak', 'Şubat', 'Mart', 'Nisan', 'Mayıs', 'Haziran', 'Temmuz', 'Ağustos', 'Eylül', 'Ekim', 'Kasım', 'Aralık'],
    skipHeader: true,
  });

  // Adjust column widths
  const colWidths = new Array(15).fill({ wch: 20 });
  worksheet['!cols'] = colWidths;

  // Style number cells and align them to the right
  const range = XLSX.utils.decode_range(worksheet['!ref']);
  for (let R = range.s.r + 1; R <= range.e.r; R++) {
    for (let C = 2; C <= 14; C++) {
      const cellRef = XLSX.utils.encode_cell({r: R, c: C});
      const cell = worksheet[cellRef];
      if (cell && !isNaN(parseFloat(cell.v))) {
        cell.t = 'n'; // Numeric type
        cell.z = '#,##0.00'; // Custom number format "###.###,00"
        cell.s = { // Style object
          alignment: {
            horizontal: 'right'
          }
        };
      }
    }
  }

  // Add the worksheet to a new workbook
  const workbook = XLSX.utils.book_new();
  XLSX.utils.book_append_sheet(workbook, worksheet, 'SalesData');

  // Write the workbook to a file
  XLSX.writeFile(workbook, fileName);
}

export default XLSXExport;
