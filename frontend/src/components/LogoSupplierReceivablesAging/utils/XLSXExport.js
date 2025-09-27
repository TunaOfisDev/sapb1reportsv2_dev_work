import * as XLSX from 'xlsx';

/**
 * Tüm benzersiz ay başlıklarını toplayıp tarihe göre sıralar (önce "Öncesi").
 */
function getUniqueMonthKeys(data) {
  const monthSet = new Set();

  data.forEach(d => {
    let monthly = d.aylik_kalan_alacak;
    try {
      if (typeof monthly === 'string') {
        monthly = JSON.parse(monthly);
      }

      if (Array.isArray(monthly)) {
        monthly.forEach(([month]) => monthSet.add(month));
      } else if (monthly && typeof monthly === 'object') {
        Object.keys(monthly).forEach(key => monthSet.add(key));
      }
    } catch (err) {
      console.error('Excel export parse error:', err);
    }
  });

  const months = Array.from(monthSet);

  const isValidMonth = (m) => /^[A-ZÇĞİÖŞÜ]{3}\d{2}$/i.test(m);
  const parsed = months
    .filter(m => m !== 'Öncesi' && isValidMonth(m))
    .map(m => {
      const ayStr = m.slice(0, 3);
      const yilStr = m.slice(3);
      const ayMap = {
        'Oca': 1, 'Şub': 2, 'Mar': 3, 'Nis': 4, 'May': 5, 'Haz': 6,
        'Tem': 7, 'Ağu': 8, 'Eyl': 9, 'Eki': 10, 'Kas': 11, 'Ara': 12
      };
      const ay = ayMap[ayStr] || 0;
      const yil = parseInt('20' + yilStr);
      return { key: m, sortValue: yil * 100 + ay };
    })
    .sort((a, b) => a.sortValue - b.sortValue)
    .map(x => x.key);

  return ['Öncesi', ...parsed];
}

/**
 * JSON verisini formatlanmış ve sıralı Excel satırlarına dönüştürür.
 */
function convertToSheetData(data, monthKeys) {
  return data.map(row => {
    const base = {
      'Cari Kod': row.cari_kod,
      'Cari Ad': row.cari_ad,
      'Güncel Bakiye': String(
        Number(row.guncel_bakiye).toLocaleString('tr-TR', {
          minimumFractionDigits: 2,
          maximumFractionDigits: 2,
          useGrouping: false
        })
      )
    };

    const monthMap = {};
    monthKeys.forEach(month => {
      monthMap[month] = '0,00';
    });

    let aylik = row.aylik_kalan_alacak;
    try {
      if (typeof aylik === 'string') {
        aylik = JSON.parse(aylik);
      }

      if (Array.isArray(aylik)) {
        aylik.forEach(([month, value]) => {
          monthMap[month] = String(Number(value).toLocaleString('tr-TR', {
            minimumFractionDigits: 2,
            maximumFractionDigits: 2,
            useGrouping: false
          }));
        });
      } else if (typeof aylik === 'object' && aylik !== null) {
        Object.entries(aylik).forEach(([month, value]) => {
          monthMap[month] = String(Number(value).toLocaleString('tr-TR', {
            minimumFractionDigits: 2,
            maximumFractionDigits: 2,
            useGrouping: false
          }));
        });
      }
    } catch (err) {
      console.warn('Excel export aylik_kalan_alacak parse hatası:', err);
    }

    return { ...base, ...monthMap };
  });
}

/**
 * Excel dosyasını oluştur ve indir.
 */
const XLSXExport = {
  exportToExcel: (data, fileName = 'Tedarikci_Odemeleri') => {
    const monthKeys = getUniqueMonthKeys(data);
    const sheetData = convertToSheetData(data, monthKeys);

    const headers = ['Cari Kod', 'Cari Ad', 'Güncel Bakiye', ...monthKeys];

    const aoa = [
      headers,
      ...sheetData.map(row =>
        headers.map(header => row[header] ?? '')
      )
    ];

    const worksheet = XLSX.utils.aoa_to_sheet(aoa);
    const workbook = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(workbook, worksheet, 'Tedarikçi Ödemeleri');
    XLSX.writeFile(workbook, `${fileName}.xlsx`);
  }
};

export default XLSXExport;
