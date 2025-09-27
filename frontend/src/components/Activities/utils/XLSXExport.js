// frontend/src/components/Activities/utils/XLSXExport.js
import * as XLSX from 'xlsx';

const exportToXLSX = (data, fileName) => {
  // Data'nın sadece gerekli kolonlarını içeren yeni bir array oluştur
  const filteredData = data.map(item => ({
    'Başlangıç Tarihi': item.baslangic_tarihi,
    'İşleyen': item.isleyen,
    'Açıklama ve İçerik': `${item.aciklama || ''} ${item.icerik || ''}`.trim(),
  }));

  const worksheet = XLSX.utils.json_to_sheet(filteredData);
  const workbook = XLSX.utils.book_new();
  XLSX.utils.book_append_sheet(workbook, worksheet, 'Sheet1');
  XLSX.writeFile(workbook, fileName);
};

export default exportToXLSX;
