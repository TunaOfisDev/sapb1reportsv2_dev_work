// frontend/src/components/CustomerSalesV2/utils/XLSXExport.js
import * as XLSX from 'xlsx';
import { formatNumber } from './FormatNumber'; // Formatlama fonksiyonunu ayrı bir dosyadan alalım (best practice)

/**
 * Verilen datayı XLSX formatında bir dosyaya dönüştürür ve tarayıcıda indirme işlemini tetikler.
 * Bu versiyon, CustomerSalesV2'nin veri yapısıyla uyumludur.
 * @param {Array<object>} data - Dışa aktarılacak veri dizisi.
 * @param {string} fileName - İndirilecek dosyanın adı.
 * @param {string} sheetName - Excel sayfasının adı.
 */
export const exportToXLSX = (data, fileName = 'rapor.xlsx', sheetName = 'Veri') => {
  if (!data || data.length === 0) {
    console.error("Dışa aktarılacak veri bulunamadı.");
    return;
  }

  // Gelen veriyi Excel'e uygun formata dönüştürüyoruz.
  const processedData = data.map(row => ({
    'Satıcı': row.satici,
    'Satış Tipi': row.satis_tipi,
    'Cari Grup': row.cari_grup,
    'Müşteri Kodu': row.musteri_kodu,
    'Müşteri Adı': row.musteri_adi,
    'Toplam Yıllık (EUR)': parseFloat(row.toplam_net_spb_eur),
    'Ocak': parseFloat(row.ocak),
    'Şubat': parseFloat(row.subat),
    'Mart': parseFloat(row.mart),
    'Nisan': parseFloat(row.nisan),
    'Mayıs': parseFloat(row.mayis),
    'Haziran': parseFloat(row.haziran),
    'Temmuz': parseFloat(row.temmuz),
    'Ağustos': parseFloat(row.agustos),
    'Eylül': parseFloat(row.eylul),
    'Ekim': parseFloat(row.ekim),
    'Kasım': parseFloat(row.kasim),
    'Aralık': parseFloat(row.aralik),
  }));

  // JSON verisini bir çalışma sayfasına dönüştür
  const worksheet = XLSX.utils.json_to_sheet(processedData);

  // Sütun genişliklerini ayarla (opsiyonel ama şık durur)
  worksheet['!cols'] = [
    { wch: 20 }, { wch: 15 }, { wch: 15 }, { wch: 15 }, { wch: 40 }, // Müşteri bilgileri
    { wch: 20 }, // Toplam
    ...Array(12).fill({ wch: 15 }) // Aylar
  ];
  
  // Sayısal hücreleri formatla
  const range = XLSX.utils.decode_range(worksheet['!ref']);
  for (let R = range.s.r + 1; R <= range.e.r; ++R) {
    for (let C = 5; C <= 17; ++C) { // Toplam ve aylık sütunları (F'den R'ye)
      const cell_address = { c: C, r: R };
      const cell_ref = XLSX.utils.encode_cell(cell_address);
      if (worksheet[cell_ref] && worksheet[cell_ref].v != null) {
          worksheet[cell_ref].t = 'n';
          worksheet[cell_ref].z = '#,##0.00';
      }
    }
  }

  // Yeni bir çalışma kitabı oluştur ve sayfayı ekle
  const workbook = XLSX.utils.book_new();
  XLSX.utils.book_append_sheet(workbook, worksheet, sheetName);

  // Dosyayı yaz ve indirmeyi tetikle
  XLSX.writeFile(workbook, fileName);
};