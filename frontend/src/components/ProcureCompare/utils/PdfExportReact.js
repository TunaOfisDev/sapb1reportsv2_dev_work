// File: frontend/src/components/ProcureCompare/utils/PdfExportReact.js

import React from 'react';
import {
  Page,
  Text,
  View,
  Document,
  Font,
  PDFDownloadLink,
  pdf
} from '@react-pdf/renderer';
import styles from './PdfExportReactStyles';
import { formatDateTime } from './DateTimeFormat';
import formatNumber from './FormatNumber';

// Font tanımı
Font.register({
  family: 'Roboto',
  fonts: [
    {
      src: 'https://fonts.gstatic.com/s/roboto/v20/KFOmCnqEu92Fr1Me5Q.ttf',
      fontWeight: 'normal',
    }
  ]
});

// Kolon yapılandırması
const columnDefs = [
  { label: 'Belge Tarih', key: 'belge_tarih', style: styles.cell },
  { label: 'Belge No', key: 'belge_no', style: styles.cell },
  { label: 'Kalem Tanımı', key: 'kalem_tanimi', style: styles.cellLarge },
  { label: 'Tedarikçi', key: 'tedarikci_ad', style: styles.cellLarge },
  { label: 'Net Fiyat (DPB)', key: 'net_fiyat_dpb', style: styles.cell },
  { label: 'Döviz', key: 'detay_doviz', style: styles.cell },
  { label: 'Teklif Fiyatları', key: 'teklif_fiyatlari_json', style: styles.cellLarge },
  { label: 'Referans Teklifler', key: 'referans_teklifler', style: styles.cellLarge },
  { label: 'Onaylayan', key: 'onaylayan', style: styles.cell },
];

// Header bileşeni
const TableHeader = () => (
  <View style={styles.tableHeader}>
    {columnDefs.map(col => (
      <Text key={col.key} style={col.style}>
        {col.label}
      </Text>
    ))}
  </View>
);

// PDF Sayfası
const PdfDocument = ({ data }) => {
  const rowsPerPage = 12;
  const pages = [];

  for (let i = 0; i < data.length; i += rowsPerPage) {
    const chunk = data.slice(i, i + rowsPerPage);
    pages.push(chunk);
  }

  return (
    <Document>
      {pages.map((pageData, pageIndex) => (
        <Page
          key={pageIndex}
          size="A4"
          style={styles.page}
          orientation="landscape"
        >
          <Text style={styles.header}>TUNA OFİS AŞ SATINALMA KARŞILAŞTIRMA RAPORU</Text>
          <Text style={{ fontSize: 9, marginBottom: 8, textAlign: 'right' }}>
            Tarih: {formatDateTime(new Date())}
          </Text>

          <View style={styles.tableContainer}>
            <TableHeader />
            {pageData.map((row, idx) => {
              const rowData = columnDefs.map(col => {
                if (col.key === 'net_fiyat_dpb') {
                  return formatNumber(row[col.key]);
                }

                if (col.key === 'teklif_fiyatlari_json') {
                  const entries = row.teklif_fiyatlari_list || [];

                  if (!entries.length) return 'Teklif Yok';

                  const minLocal = Math.min(...entries.map(e => e.local_price));
                  const EPSILON = 0.001;

                  return entries
                    .sort((a, b) => a.local_price - b.local_price)
                    .map(entry => {
                      const isMin = Math.abs(entry.local_price - minLocal) < EPSILON;
                      const label = isMin ? `* ${entry.firma}` : entry.firma;
                      const value = `${formatNumber(entry.fiyat)} ${entry.doviz}`;
                      return `${label}\n${value}`;
                    })
                    .join('\n\n');
                }

                if (col.key === 'referans_teklifler') {
                  try {
                    const parsed = JSON.parse(row[col.key]);
                    return Array.isArray(parsed) && parsed.length > 0 ? parsed.join(', ') : 'Yok';
                  } catch {
                    return 'Yok';
                  }
                }

                if (col.key === 'onaylayan') {
                  return ''; // Boş hücre
                }

                return row[col.key] || '-';
              });

              return (
                <View style={styles.tableRow} key={idx}>
                  {rowData.map((value, colIdx) => (
                    <Text key={colIdx} style={columnDefs[colIdx].style}>
                      {value}
                    </Text>
                  ))}
                </View>
              );
            })}
          </View>

          <Text
            style={styles.footer}
            render={({ pageNumber, totalPages }) =>
              `Sayfa ${pageNumber} / ${totalPages}`
            }
          />
        </Page>
      ))}
    </Document>
  );
};

// PDF İndir Butonu
export const PdfExportButton = ({ data }) => (
  <PDFDownloadLink
    document={<PdfDocument data={data} />}
    fileName="satin-alma-karsilastirma.pdf"
  >
    {({ loading }) => (loading ? 'PDF hazırlanıyor...' : 'PDF İndir')}
  </PDFDownloadLink>
);

// Harici export fonksiyonu
export const handleExportPDF = async (data) => {
  const blob = await pdf(<PdfDocument data={data} />).toBlob();
  const link = document.createElement('a');
  link.href = URL.createObjectURL(blob);
  link.download = 'satin-alma-karsilastirma.pdf';
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
};

export default PdfExportButton;
