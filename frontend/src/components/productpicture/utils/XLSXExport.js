// frontend/src/components/productpicture/utils/XLSXExport.js
import * as XLSX from 'xlsx';

const exportToExcel = (data, fileName, headers) => {
  // Yeni bir çalışma kitabı oluştur
  const wb = XLSX.utils.book_new();

  // Verileri JSON'dan bir çalışma sayfasına dönüştür
  const ws = XLSX.utils.json_to_sheet(data, { skipHeader: true });
  
  // Manuel başlıkları ayarla
  headers.forEach((header, index) => {
    const cell_address = {c: index, r: 0};
    const cell_ref = XLSX.utils.encode_cell(cell_address);
    ws[cell_ref] = { t: 's', v: header };
  });
  
  // Çalışma sayfasını çalışma kitabına ekle
  XLSX.utils.book_append_sheet(wb, ws, 'Sheet1');
  
  // Çalışma sayfası sütun genişliklerini ayarla
  ws['!cols'] = headers.map(_ => ({ width: 15 }));
  
  // Çalışma kitabını bir XLSX dosyasına yaz
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