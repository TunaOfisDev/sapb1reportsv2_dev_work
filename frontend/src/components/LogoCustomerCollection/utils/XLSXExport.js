// frontend/src/components/LogoCustomerCollection/utils/XLSXExport.js
import * as XLSX from 'xlsx';

/* ---------------- yardımcı: benzersiz ay etiketleri ---------------- */
function getUniqueMonthKeys(data) {
  const monthSet = new Set();

  data.forEach(r => {
    let monthly = r.aylik_kalan_borc;
    try {
      if (typeof monthly === 'string') monthly = JSON.parse(monthly);

      if (Array.isArray(monthly)) {
        monthly.forEach(([m]) => monthSet.add(m));
      } else if (monthly && typeof monthly === 'object') {
        Object.keys(monthly).forEach(m => monthSet.add(m));
      }
    } catch (e) { console.warn('month parse', e); }
  });

  /* “Öncesi” haricindeki ayları kronolojik sırala */
  const ayMap = {
    Oca: 1, Şub: 2, Mar: 3, Nis: 4, May: 5, Haz: 6,
    Tem: 7, Ağu: 8, Eyl: 9, Eki: 10, Kas: 11, Ara: 12,
  };

  const sorted = [...monthSet]
    .filter(m => m !== 'Öncesi')
    .map(m => ({
      key: m,
      sort: (() => {
        const ay = ayMap[m.slice(0, 3)] ?? 0;
        const yy = Number('20' + m.slice(3)); // “25” → 2025
        return yy * 100 + ay;
      })(),
    }))
    .sort((a, b) => a.sort - b.sort)
    .map(x => x.key);

  return ['Öncesi', ...sorted];
}

/* ---------------- satırları AOArray’e dönüştür ---------------- */
function convertToSheetData(data, monthKeys) {
  const fmt = n => String(Number(n).toLocaleString('tr-TR', {
    minimumFractionDigits: 2, maximumFractionDigits: 2, useGrouping: false,
  }));

  return data.map(r => {
    const base = {
      'Cari Kod':     r.cari_kod,
      'Cari Ad':      r.cari_ad,
      'Güncel Bakiye': fmt(r.guncel_bakiye),
    };

    /* ay kolonları başlangıçta 0,00 */
    const monthCols = Object.fromEntries(monthKeys.map(k => [k, '0,00']));

    /* gelen aylık veriyi işle */
    let monthly = r.aylik_kalan_borc;
    try {
      if (typeof monthly === 'string') monthly = JSON.parse(monthly);

      if (Array.isArray(monthly)) {
        monthly.forEach(([m, v]) => { monthCols[m] = fmt(v); });
      } else if (monthly && typeof monthly === 'object') {
        Object.entries(monthly).forEach(([m, v]) => { monthCols[m] = fmt(v); });
      }
    } catch (e) { console.warn('aylik_kalan_borc parse', e); }

    return { ...base, ...monthCols };
  });
}

/* ---------------- ana export nesnesi ---------------- */
const XLSXExport = {
  exportToExcel: (data, fileName = 'Musteri_Yaslandirma_Ozeti') => {
    if (!data?.length) { alert('Aktarılacak veri yok.'); return; }

    const monthKeys = getUniqueMonthKeys(data);
    const sheetRows = convertToSheetData(data, monthKeys);

    /* başlıklar: sabit + dinamik aylar */
    const headers = ['Cari Kod', 'Cari Ad', 'Güncel Bakiye', ...monthKeys];

    /* AOArray: [headers, ...rows] */
    const aoa = [
      headers,
      ...sheetRows.map(row => headers.map(h => row[h] ?? '')),
    ];

    const ws  = XLSX.utils.aoa_to_sheet(aoa);
    const wb  = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(wb, ws, 'Müşteri Yaşlandırma');

    XLSX.writeFile(wb, `${fileName}.xlsx`);
  },
};

export default XLSXExport;
