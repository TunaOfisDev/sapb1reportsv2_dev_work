// frontend/src/components/DynamicReport/utils/DynamicXLSXExport.js
import * as XLSX from 'xlsx';

const exportToExcel = (data, fileName, headers) => {
  // Yeni bir workbook oluştur
  const wb = XLSX.utils.book_new();

  // Veriyi JSON'dan worksheet'e dönüştür
  const ws = XLSX.utils.json_to_sheet(data, { skipHeader: true });
  
  // Manuel başlıkları ayarla
  headers.forEach((header, index) => {
    const cell_address = {c: index, r: 0};
    const cell_ref = XLSX.utils.encode_cell(cell_address);
    ws[cell_ref] = { t: 's', v: header };
  });
  
  // Worksheet'i workbook'a ekle
  XLSX.utils.book_append_sheet(wb, ws, 'Sheet1');
  
  // Çalışma sayfası sütun genişliklerini ayarla
  ws['!cols'] = headers.map(_ => ({ width: 15 }));
  
  // Workbook'u XLSX dosyasına yaz
  const excelBuffer = XLSX.write(wb, { bookType: 'xlsx', type: 'array' });

  // Blob nesnesi oluştur ve indir
  const blob = new Blob([excelBuffer], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' });
  const url = window.URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = fileName || 'export.xlsx';
  a.click();

  // URL'i temizle
  window.URL.revokeObjectURL(url);
};


export default exportToExcel;
