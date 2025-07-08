// path: frontend/src/components/StockCardIntegration/hooks/useBulkUpload.js
import { useState } from 'react';
import * as XLSX from 'xlsx';

/* “890,99” → “890.99” */
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

const useBulkUpload = () => {
  const [previewData, setPreviewData] = useState([]);
  const [fileError, setFileError] = useState(null);

  /* --------------------------------------------------
   * Dosya okuma
   * ------------------------------------------------ */
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

        /* ---- Başlık doğrulama ---- */
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

        /* ---- Satır dönüştürme ---- */
        const sanitized = rawJson.map((row) => {
          /* Eğer bir şekilde “Price” kolonu geldiyse “Fiyat”a taşı */
          if ('Price' in row && !row.Fiyat) {
            row.Fiyat = row.Price;
          }
          /* Fiyatı normalize et */
          row.Fiyat = normalizePrice(row.Fiyat);
          /* Temizlik – Price kolonunu sil */
          delete row.Price;
          return row;
        });

        setPreviewData(sanitized);
      } catch (err) {
        console.error('Dosya okuma hatası:', err);
        setFileError(
          'Geçersiz dosya formatı. Lütfen geçerli bir Excel dosyası (.xlsx) yükleyin.',
        );
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
