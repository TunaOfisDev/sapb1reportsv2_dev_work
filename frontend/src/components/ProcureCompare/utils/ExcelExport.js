// File: frontend/src/components/ProcureCompare/utils/ExcelExport.js

import * as XLSX from 'xlsx';
import { formatDate } from './DateTimeFormat';
import formatNumberExcelExport from './FormatNumberExcelExport';

const exportToExcel = (dataInput, fileName = 'satin-alma-karsilastirma.xlsx') => {
  if (!dataInput) return;

  // Eğer react-table'dan filteredRows gelirse, onu kullan
  const data = Array.isArray(dataInput)
  ? dataInput
  : Array.isArray(dataInput.filteredRows)
    ? dataInput.filteredRows
    : [];

  if (!data || !Array.isArray(data)) return;

  const excelRows = data.map(row => {
    let teklifFiyatlariParsed = '-';
    try {
      const parsed = JSON.parse(row.teklif_fiyatlari_json);
      const entries = Object.entries(parsed);
      const fiyatListesi = entries.map(([firma, fiyat]) => {
        const match = fiyat.match(/^([\d.,]+)\s*(\w{3})$/);
        if (!match) return `${firma}: ${fiyat}`;
        const [, numberPart, currency] = match;
        const numeric = parseFloat(numberPart.replace(',', '.').replace(/[^\d.]/g, ''));
        return `${firma}: ${formatNumberExcelExport(numeric)} ${currency}`;
      });
      teklifFiyatlariParsed = fiyatListesi.join('\n');
    } catch (e) {
      teklifFiyatlariParsed = 'Hatalı JSON';
    }

    return {
      'Belge Tarih': formatDate(row.belge_tarih),
      'Belge No': row.belge_no,
      'Kalem Tanimi': row.kalem_tanimi,
      'Tedarikçi': row.tedarikci_ad,
      'Net Fiyat (DPB)': formatNumberExcelExport(row.net_fiyat_dpb),
      'Döviz': row.detay_doviz,
      'Teklif Fiyatları': teklifFiyatlariParsed,
      'Referans Teklifler': (() => {
        try {
          const list = JSON.parse(row.referans_teklifler);
          return Array.isArray(list) ? list.join(', ') : row.referans_teklifler;
        } catch {
          return row.referans_teklifler || '-';
        }
      })()
    };
  });

  const worksheet = XLSX.utils.json_to_sheet(excelRows);
  const workbook = XLSX.utils.book_new();
  XLSX.utils.book_append_sheet(workbook, worksheet, 'Satın Alma');

  XLSX.writeFile(workbook, fileName);
};

export default exportToExcel;
