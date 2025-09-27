// frontend/src/components/OpenOrderDocSum/utils/XLSXExport.js
import * as XLSX from 'xlsx';

function formatNumber(number) {
  return parseFloat(number);  // Sayıyı doğrudan float olarak dönüştür
}

function formatDate(date) {
  const dateObj = new Date(date);
  return new Intl.DateTimeFormat('tr-TR', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit'
  }).format(dateObj).replace(/\./g, '-').replace(/\s/g, '');
}

function sanitizeText(text) {
  return text ? text.toString().replace(/[\u0000-\u001F\u007F-\u009F]/g, '') : '';  // Metni temizleyin ve geçersiz karakterleri kaldırın
}

function convertToSheetData(data) {
  return data.map(d => ({
    Belge_No: d.belge_no,
    Statu: d.belge_durum,
    Satıcı: d.satici,
    Belge_Tarihi: formatDate(d.belge_tarih),
    Teslim_Tarihi: formatDate(d.teslim_tarih),
    Müşteri_Kodu: d.musteri_kod,
    Müşteri_Adı: d.musteri_ad,
    Satış_Tipi: d.satis_tipi,
    İskonto: formatNumber(d.belge_iskonto_oran),
    NetTutarYPB: formatNumber(d.net_tutar_ypb),
    NetTutarSPB: formatNumber(d.net_tutar_spb),
    AcikTutarYPB: formatNumber(d.acik_net_tutar_ypb),
    AcikTutarSPB: formatNumber(d.acik_net_tutar_spb),
    Belge_Aciklamasi: sanitizeText(d.belge_aciklamasi),  // Metni temizleyin
  }));
}

const XLSXExport = {
  exportToExcel: (data, fileName) => {
    const sheetData = convertToSheetData(data);
    const ws = XLSX.utils.json_to_sheet(sheetData);

    // Hücre biçimlendirme ve stil uygulama
    const range = XLSX.utils.decode_range(ws['!ref']);
    for(let R = range.s.r; R <= range.e.r; ++R) {
      for(let C = range.s.c; C <= range.e.c; ++C) {
        const cell_address = {c:C, r:R};
        const cell_ref = XLSX.utils.encode_cell(cell_address);
        const cell = ws[cell_ref];
        if(cell && (cell_ref.includes('C') || cell_ref.includes('D'))) {  
          cell.s = {
            alignment: {
              horizontal: 'right'
            }
          };
        } else if (cell && !isNaN(cell.v)) {  // Sayısal değerler için sayı formatı uygula
          cell.t = 'n';  // Hücre tipini sayısal yap
          cell.z = '###0,00';  // Sayısal biçimlendirme
        }
      }
    }

    const wb = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(wb, ws, 'Açık Sipariş Özeti Nakliye');
    XLSX.writeFile(wb, `${fileName}.xlsx`);
  }
};

export default XLSXExport;
