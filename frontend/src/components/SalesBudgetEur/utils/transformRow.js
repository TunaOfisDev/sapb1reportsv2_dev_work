// frontend/src/components/SalesBudgetEur/utils/transformRow.js
// Aylık verileri düz (flatten) alanlara çevirip UpperTotal & table için hazırlayan fonksiyon

const monthMap = [
  'oca', 'sub', 'mar', 'nis', 'may', 'haz',
  'tem', 'agu', 'eyl', 'eki', 'kas', 'ara'
];

export default function transformRow(row = {}) {
  const toplamGercek = parseFloat(row.toplam_gercek_eur || 0);
  const toplamHedef = parseFloat(row.toplam_hedef_eur || 0);
  const yuzdeOran = toplamHedef > 0 ? (toplamGercek / toplamHedef) * 100 : 0;

  const flat = {
    satici: row.satici || 'Bilinmeyen',
    yil: row.yil,
    toplam_gercek: toplamGercek,
    toplam_hedef: toplamHedef,
    yuzde_oran: yuzdeOran,
    toplam_iptal_eur: parseFloat(row.toplam_iptal_eur || 0),
    toplam_elle_kapanan_eur: parseFloat(row.toplam_elle_kapanan_eur || 0),
    kapali_sip_list: row.kapali_sip_list || ''
  };

  (row.aylik_veriler || []).forEach(({ ay, gercek_tutar = 0, hedef_tutar = 0 }) => {
    const base = monthMap[ay - 1];
    flat[`${base}_gercek`] = parseFloat(gercek_tutar || 0);
    flat[`${base}_hedef`] = parseFloat(hedef_tutar || 0);
  });

  // Eksik aylar için 0 ataması
  monthMap.forEach(m => {
    flat[`${m}_gercek`] = flat[`${m}_gercek`] || 0;
    flat[`${m}_hedef`] = flat[`${m}_hedef`] || 0;
  });

  return flat;
}
