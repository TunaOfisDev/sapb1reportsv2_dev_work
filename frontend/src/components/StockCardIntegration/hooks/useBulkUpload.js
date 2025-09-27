// path: frontend/src/components/StockCardIntegration/hooks/useBulkUpload.js
import { useState } from 'react';
import * as XLSX from 'xlsx';

/* --------------------------------------------------
 * Sabitler
 * ------------------------------------------------ */
export const MAX_BULK_ROWS = 20; // başlık hariç izin verilen en yüksek satır sayısı

/* “890,99” → “890.99”  */
const normalizePrice = (value) =>
  typeof value === 'string' ? value.replace(',', '.') : value;

/* Beklenen başlık seti – sıralama önemsiz */
const EXPECTED_HEADERS = new Set([
  'Kalem Kodu',
  'Kalem Tanımı',
  'Satış Ölçü Birimi',
  'Ürün Grubu',
  'KDV Grubu',
  'Fiyat',
  'Para Birimi',
  'Eski Bileşen Kod',
]);

/* --------------------------------------------------
 * Hook
 * ------------------------------------------------ */
const useBulkUpload = () => {
  const [previewData, setPreviewData] = useState([]);
  const [fileError, setFileError] = useState(null);

  /* ----------------------------------------------
   * Dosya okuma & doğrulama
   * -------------------------------------------- */
  const handleFileUpload = (event) => {
    const file = event.target.files?.[0];
    setFileError(null);

    if (!file) return;

    const reader = new FileReader();

    reader.onload = (e) => {
      try {
        const data = new Uint8Array(e.target.result);
        const workbook = XLSX.read(data, { type: 'array' });

        const firstSheetName = workbook.SheetNames[0];
        const worksheet = workbook.Sheets[firstSheetName];
        const rawJson = XLSX.utils.sheet_to_json(worksheet, { defval: '' });

        /* 1) Başlık doğrulama */
        const headersInFile = new Set(Object.keys(rawJson[0] || {}));
        const missing = [...EXPECTED_HEADERS].filter((h) => !headersInFile.has(h));

        if (missing.length) {
          setFileError(
            `Excel dosyasında eksik başlık(lar): ${missing.join(', ')}. ` +
              'Lütfen örnek şablonu kullanın.',
          );
          setPreviewData([]);
          return;
        }

        /* 2) Satır sayısı (başlık hariç) kontrolü */
        const rowCount = rawJson.length; // sheet_to_json verisi başlık satırını kapsamaz
        if (rowCount > MAX_BULK_ROWS) {
          setFileError(
            `Başlık hariç en fazla ${MAX_BULK_ROWS} satır yükleyebilirsiniz. (Gönderilen: ${rowCount})`,
          );
          setPreviewData([]);
          return;
        }

        /* 3) Satır dönüştürme */
        const sanitized = rawJson.map((row) => {
          /* Price → Fiyat düzeltmesi (eski şablon uyumu) */
          if ('Price' in row && !row.Fiyat) {
            row.Fiyat = row.Price;
          }
          row.Fiyat = normalizePrice(row.Fiyat);
          delete row.Price; // temizlik
          return row;
        });

        setPreviewData(sanitized);
      } catch (err) {
        console.error('Dosya okuma hatası:', err);
        setFileError(
          'Geçersiz dosya formatı. Lütfen geçerli bir Excel dosyası (.xlsx) yükleyin.',
        );
        setPreviewData([]);
      }
    };

    reader.readAsArrayBuffer(file);
  };

  /* Yüklemeyi sıfırla */
  const resetUpload = () => {
    setPreviewData([]);
    setFileError(null);
  };

  return {
    previewData,
    fileError,
    handleFileUpload,
    resetUpload,
  };
};

export default useBulkUpload;
