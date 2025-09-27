// frontend/src/components/GirsbergerOrdrOpqt/utils/XLSXExport.js
import * as XLSX from 'xlsx';

function formatNumber(number) {
  return parseFloat(number);
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
  if (!text) return '';

  return Array.from(text.toString())
    .filter(char => {
      const code = char.charCodeAt(0);
      return (code >= 32 && code <= 126) || (code >= 160); // Geçerli karakter aralıkları
    })
    .join('');
}

function convertToSheetData(data) {
  return data.map(d => ({
    BelgeNo: d.belge_no,
    KaynakDetayNo: d.salma_teklif_kaynak_detay_no,
    Satıcı: d.satici,
    BelgeTarih: formatDate(d.belge_tarih),
    TeslimTarih: formatDate(d.teslim_tarih),
    MüşteriKod: d.musteri_kod,
    MüşteriAd: d.musteri_ad,
    SatışTipi: d.satis_tipi,
    SatırStatus: d.satir_status,
    KalemKod: d.kalem_kod,
    KalemTanımı: sanitizeText(d.kalem_tanimi), // Metni temizleyin
    SipMiktar: formatNumber(d.sip_miktar),
    SevkMiktar: formatNumber(d.sevk_miktar),
    KalanMiktar: formatNumber(d.kalan_miktar),
    ListeFiyatDPB: formatNumber(d.liste_fiyat_dpb),
    DetayKur: formatNumber(d.detay_kur),
    DetayDöviz: d.detay_doviz,
    IskOran: formatNumber(d.iskonto_oran),
    NetFiyatDPB: formatNumber(d.net_fiyat_dpb),
    NetTutarYPB: formatNumber(d.net_tutar_ypb),
    AçıkNetTutarYPB: formatNumber(d.acik_net_tutar_ypb),
    SalmaTeklifTedarikçiKod: d.salma_teklif_tedarikci_kod,
    SalmaTeklifTedarikçiAd: d.salma_teklif_tedarikci_ad,
    SalmaTeklifNo: d.salma_teklif_no,
    SalmaTeklifKalemNo: d.salma_teklif_kalem_no,
    SalmaTeklifMiktar: formatNumber(d.salma_teklif_miktar)
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
        
        if (cell && !isNaN(cell.v)) {  // Sayısal değerler için sayı formatı uygula
          cell.t = 'n';  // Hücre tipini sayısal yap
          cell.z = '###0,00';  // Sayısal biçimlendirme
          cell.s = {
            alignment: {
              horizontal: 'right'
            }
          };
        }
      }
    }

    const wb = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(wb, ws, 'GirsbergerOrdrOpqtReport');
    XLSX.writeFile(wb, `${fileName}.xlsx`);
  }
};

export default XLSXExport;
