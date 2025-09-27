// frontend/src/components/SalesOrderDocSum/utils/CopyToExcel.js
import * as XLSX from 'xlsx';

function formatDate(date) {
  const dateObj = new Date(date);
  return new Intl.DateTimeFormat('tr-TR', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit'
  }).format(dateObj);
}

function convertToSheetData(orderDetails, masterDetail) {
  // Header bilgileri
  const headerRows = [
    ['Sipariş Detayları'],
    ['Müşteri Ad:', masterDetail.musteri_ad || ''],
    ['Sipariş No:', masterDetail.sip_no || ''],
    ['Belge Tarihi:', formatDate(masterDetail.belge_tarihi)],
    [], // Boş satır
  ];

  // Tablo başlıkları
  const tableHeaders = [
    'No',
    'KalemKodu',
    'KalemTanimi',
    'Miktar',
    'Fiyat(DPB)',
    'IskOran',
    'NetTutar(SPB)'
  ];

  // Detay satırları
  const detailRows = orderDetails.map((detail, index) => [
    index,
    detail.kalem_kod || '',
    detail.kalem_tanimi || '',
    { v: detail.siparis_miktari || 0, t: 'n' },
    { v: detail.liste_fiyat_dpb || 0, t: 'n' },
    { v: detail.iskonto_oran || 0, t: 'n' },
    { v: detail.net_tutar_spb || 0, t: 'n' }
  ]);

  // Toplam satırı için hesaplama
  const totals = orderDetails.reduce((acc, curr) => ({
    netTotal: acc.netTotal + (Number(curr.net_tutar_spb) || 0),
    quantity: acc.quantity + (Number(curr.siparis_miktari) || 0)
  }), { netTotal: 0, quantity: 0 });

  // Toplam satırı
  const totalRow = [
    'TOPLAM',
    '',
    '',
    { v: totals.quantity, t: 'n' },
    '',
    '',
    { v: totals.netTotal, t: 'n' }
  ];

  return {
    data: [...headerRows, tableHeaders, ...detailRows, [], totalRow],
    startCell: { r: 0, c: 0 },
    endCell: { r: headerRows.length + detailRows.length + 1, c: tableHeaders.length - 1 }
  };
}

const CopyToExcel = {
  exportOrderDetails: (orderDetails, masterDetail) => {
    try {
      const wb = XLSX.utils.book_new();
      const { data, startCell, endCell } = convertToSheetData(orderDetails, masterDetail);
      const ws = XLSX.utils.aoa_to_sheet(data);

      // Sütun genişlikleri
      ws['!cols'] = [
        { wch: 5 },     // No
        { wch: 25 },    // KalemKodu
        { wch: 70 },    // KalemTanimi
        { wch: 10 },    // Miktar
        { wch: 12 },    // Fiyat
        { wch: 10 },    // IskOran
        { wch: 15 }     // NetTutar
      ];

      // Başlık stili
      ws['A1'].s = {
        font: { bold: true, size: 14 },
        alignment: { horizontal: 'center' }
      };

      // Tablo başlıkları için stil
      const headerRowIndex = 5;
      for (let C = startCell.c; C <= endCell.c; C++) {
        const cellRef = XLSX.utils.encode_cell({ r: headerRowIndex, c: C });
        ws[cellRef].s = {
          font: { bold: true, color: { rgb: "FFFFFF" } },
          fill: { fgColor: { rgb: "2C4E6C" }, patternType: 'solid' },
          alignment: { horizontal: 'center', vertical: 'center' }
        };
      }

      // Sayısal değerler için stil ve format
      const numericColumns = [3, 4, 5, 6]; // Miktar, Fiyat, IskOran, NetTutar sütunları
      for (let R = headerRowIndex + 1; R <= endCell.r; R++) {
        for (let C = 0; C < 7; C++) {
          const cellRef = XLSX.utils.encode_cell({ r: R, c: C });
          if (!ws[cellRef]) continue;

          if (numericColumns.includes(C)) {
            ws[cellRef].z = '#.##0,00'; // Türkçe sayı formatı
            ws[cellRef].s = {
              alignment: { horizontal: 'right' },
              font: { name: 'Arial' }
            };
          } else {
            ws[cellRef].s = {
              alignment: { 
                horizontal: C === 2 ? 'left' : 'center',
                vertical: 'center'
              }
            };
          }
        }
      }

      // Toplam satırı için özel stil
      const totalRowIndex = endCell.r;
      for (let C = 0; C <= endCell.c; C++) {
        const cellRef = XLSX.utils.encode_cell({ r: totalRowIndex, c: C });
        if (ws[cellRef]) {
          ws[cellRef].s = {
            font: { bold: true },
            border: { top: { style: 'thin', color: { rgb: "000000" } } },
            alignment: { 
              horizontal: numericColumns.includes(C) ? 'right' : 'center'
            }
          };
        }
      }

      // Worksheet'i workbook'a ekle
      XLSX.utils.book_append_sheet(wb, ws, 'Sipariş Detay');

      // Dosya adı için tarih oluştur
      const today = new Date();
      const dateStr = today.toLocaleDateString('tr-TR').replace(/\./g, '');
      const fileName = `SiparisDetay_${masterDetail.sip_no}_${dateStr}`;

      // Excel dosyasını kaydet
      XLSX.writeFile(wb, `${fileName}.xlsx`);

      return true;
    } catch (error) {
      console.error('Excel export hatası:', error);
      return false;
    }
  }
};

export default CopyToExcel;