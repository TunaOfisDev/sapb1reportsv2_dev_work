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
  if (typeof text !== 'string') {
    text = text != null ? String(text) : '';
  }
  // Yazdırılabilir olmayan karakterleri ve kontrol karakterlerini kaldır
  return text.replace(/[^\x20-\x7E\xA0-\xFF]/g, '');
}

function convertToSheetData(rows) {
  return rows.map(row => {
    const originalData = row.original;
    return {
      Belge_No: originalData.belge_no,
      Statu: originalData.belge_durum,
      Satıcı: originalData.satici,
      Belge_Tarihi: formatDate(originalData.belge_tarih),
      Teslim_Tarihi: formatDate(originalData.teslim_tarih),
      Müşteri_Kodu: originalData.musteri_kod,
      Müşteri_Adı: originalData.musteri_ad,
      Satış_Tipi: originalData.satis_tipi,
      İskonto: formatNumber(originalData.belge_iskonto_oran),
      NetTutarYPB: formatNumber(originalData.net_tutar_ypb),
      NetTutarSPB: formatNumber(originalData.net_tutar_spb),
      AcikTutarYPB: formatNumber(originalData.acik_net_tutar_ypb),
      AcikTutarSPB: formatNumber(originalData.acik_net_tutar_spb),
      Belge_Aciklamasi: sanitizeText(originalData.belge_aciklamasi),
    };
  });
}

const XLSXExport = {
  exportToExcel: (rows, fileName, totals = null) => {
    const sheetData = convertToSheetData(rows);

    // Toplam satırını ekle (eğer varsa)
    if (totals) {
      sheetData.push({
        Belge_No: 'TOPLAM',
        Statu: '',
        Satıcı: '',
        Belge_Tarihi: '',
        Teslim_Tarihi: '',
        Müşteri_Kodu: '',
        Müşteri_Adı: '',
        Satış_Tipi: '',
        İskonto: '',
        NetTutarYPB: formatNumber(totals.net_tutar_ypb),
        NetTutarSPB: formatNumber(totals.net_tutar_spb),
        AcikTutarYPB: formatNumber(totals.acik_net_tutar_ypb),
        AcikTutarSPB: formatNumber(totals.acik_net_tutar_spb),
        Belge_Aciklamasi: '',
      });
    }

    const ws = XLSX.utils.json_to_sheet(sheetData);

    // Header stilini ayarla
    ws['!cols'] = [
      { wch: 15 },  // Belge No
      { wch: 10 },  // Statu
      { wch: 15 },  // Satıcı
      { wch: 12 },  // Belge Tarihi
      { wch: 12 },  // Teslim Tarihi
      { wch: 15 },  // Müşteri Kodu
      { wch: 30 },  // Müşteri Adı
      { wch: 15 },  // Satış Tipi
      { wch: 10 },  // İskonto
      { wch: 15 },  // NetTutarYPB
      { wch: 15 },  // NetTutarSPB
      { wch: 15 },  // AcikTutarYPB
      { wch: 15 },  // AcikTutarSPB
      { wch: 30 },  // Belge Açıklaması
    ];

    // Hücre biçimlendirme ve stil uygulama
    const range = XLSX.utils.decode_range(ws['!ref']);
    for(let R = range.s.r; R <= range.e.r; ++R) {
      for(let C = range.s.c; C <= range.e.c; ++C) {
        const cell_address = {c:C, r:R};
        const cell_ref = XLSX.utils.encode_cell(cell_address);
        const cell = ws[cell_ref];
        
        // Header satırı için stil
        if (R === 0) {
          cell.s = {
            fill: { fgColor: { rgb: "2C4E6C" }, patternType: 'solid' },
            font: { color: { rgb: "FFFFFF" }, bold: true },
            alignment: { horizontal: 'center', vertical: 'center' }
          };
        }
        // Toplam satırı için stil
        else if (totals && R === range.e.r) {
          cell.s = {
            font: { bold: true },
            border: {
              top: { style: 'thin', color: { rgb: "000000" } }
            }
          };
        }
        // Sayısal değerler için stil
        else if (cell && !isNaN(cell.v) && C >= 8) { // İskonto ve sonrası sütunlar
          cell.t = 'n';
          cell.z = '#,##0.00';
          cell.s = {
            alignment: { horizontal: 'right' }
          };
        }
        // Tarih sütunları için stil
        else if (C === 3 || C === 4) { // Belge Tarihi ve Teslim Tarihi
          cell.s = {
            alignment: { horizontal: 'center' }
          };
        }
      }
    }

    const wb = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(wb, ws, 'Açık Sipariş Özeti');
    
    // Dosya adına tarih ekle
    const today = new Date();
    const dateStr = today.toLocaleDateString('tr-TR').replace(/\./g, '');
    const fullFileName = `${fileName}_${dateStr}`;
    
    XLSX.writeFile(wb, `${fullFileName}.xlsx`);
  }
};

export default XLSXExport;