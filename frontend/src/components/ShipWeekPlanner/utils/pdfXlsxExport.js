// frontend/src/components/ShipWeekPlanner/utils/pdfXlsxExport.js
import React from 'react';
import { Page, Text, View, Document, StyleSheet, Font, PDFDownloadLink, pdf } from '@react-pdf/renderer';
import * as XLSX from 'xlsx';
import groupByDayOfWeek from './groupByDayOfWeek';
import dayjs from 'dayjs';
import 'dayjs/locale/tr';

// Roboto font kaydı 
Font.register({
  family: 'Roboto',
  src: '/fonts/roboto.ttf', // public/fonts/roboto.ttf olacak şekilde ayarla
});


// PDF Stilleri
const styles = StyleSheet.create({
   page: { 
       padding: 20,
       fontFamily: 'Roboto',
       backgroundColor: 'white',
   },
   header: { 
       fontSize: 14, 
       marginBottom: 10,
       textAlign: 'center', 
       fontWeight: 'bold',
       color: '#333',
   },
   tableContainer: {
       flexDirection: 'column',
       width: '100%',
       marginTop: 5,
   },
   tableHeader: {
       flexDirection: 'row',
       backgroundColor: '#1976d2',
       borderBottomWidth: 0.2,
       borderBottomColor: '#666',
       borderTopWidth: 0.2,
       borderTopColor: '#666',
   },
   tableRow: {
       flexDirection: 'row',
       borderBottomWidth: 0.2,
       borderBottomColor: '#666',
       minHeight: 20,
   },
   cellHeader: {
       flex: 1,
       padding: 2,
       fontSize: 8,
       color: 'white',
       textAlign: 'center',
       borderLeftWidth: 0.2,
       borderLeftColor: '#666',
       borderRightWidth: 0.2,
       borderRightColor: '#666',
   },
   cell: {
       flex: 1,
       padding: 2,
       fontSize: 7,
       textAlign: 'left',
       borderLeftWidth: 0.2,
       borderLeftColor: '#666',
       borderRightWidth: 0.2,
       borderRightColor: '#666',
   },
   cellLarge: {
       flex: 1.5,
       padding: 2,
       fontSize: 7,
       textAlign: 'left',
       borderLeftWidth: 0.2,
       borderLeftColor: '#666',
       borderRightWidth: 0.2,
       borderRightColor: '#666',
   },
   footer: {
       position: 'absolute',
       bottom: 20,
       left: 20,
       right: 20,
       fontSize: 8,
       textAlign: 'left',
       color: '#666',
   },
});

// Tarih formatı
const formatDate = (date) => (date ? dayjs(date).format('DD.MM.YYYY') : '');

// PDF Document bileşeni
const PdfDocument = ({ data }) => {
   const groupedOrders = groupByDayOfWeek(data.orders);
   const orders = Object.entries(groupedOrders).flatMap(([dayName, orders]) =>
       orders.map(order => ({
           day: dayName,
           status: order.order_status || '-',
           orderNumber: order.order_number || '-',
           customerName: order.customer_name || '-',
           orderDate: formatDate(order.order_date),
           shipmentDate: formatDate(order.shipment_date),
           salesPerson: order.sales_person || '-',
           shipmentDetails: order.shipment_details || '-',
           shipmentNotes: order.shipment_notes || '-',
       }))
   );

   return (
       <Document>
           <Page size="A4" style={styles.page}>
               <Text style={styles.header}>Haftalık Sevk Planlama ({data.week}. Hafta)</Text>
               
               <View style={styles.tableContainer}>
                   <View style={styles.tableHeader}>
                       <Text style={styles.cellHeader}>Gün</Text>
                       <Text style={styles.cellHeader}>Statu</Text>
                       <Text style={styles.cellHeader}>Sipariş No</Text>
                       <Text style={styles.cellLarge}>Müşteri Adı</Text>
                       <Text style={styles.cellHeader}>Sipariş Tarihi</Text>
                       <Text style={styles.cellHeader}>Sevk Tarihi</Text>
                       <Text style={styles.cellHeader}>Satıcı</Text>
                       <Text style={styles.cellLarge}>Sevk Adresi</Text>
                       <Text style={styles.cellLarge}>Sevk Notları</Text>
                   </View>

                   {orders.map((order, index) => (
                       <View key={index} style={styles.tableRow}>
                           <Text style={styles.cell}>{order.day}</Text>
                           <Text style={styles.cell}>{order.status}</Text>
                           <Text style={styles.cell}>{order.orderNumber}</Text>
                           <Text style={styles.cellLarge}>{order.customerName}</Text>
                           <Text style={styles.cell}>{order.orderDate}</Text>
                           <Text style={styles.cell}>{order.shipmentDate}</Text>
                           <Text style={styles.cell}>{order.salesPerson}</Text>
                           <Text style={styles.cellLarge}>{order.shipmentDetails}</Text>
                           <Text style={styles.cellLarge}>{order.shipmentNotes}</Text>
                       </View>
                   ))}
               </View>

               <Text
                   style={styles.footer}
                   render={({ pageNumber, totalPages }) =>
                       `Sayfa ${pageNumber} / ${totalPages}`
                   }
               />
           </Page>
       </Document>
   );
};

// PDF İndirme Butonu
export const PdfExportButton = ({ data }) => (
   <PDFDownloadLink document={<PdfDocument data={data} />} fileName={`Sevk_Plani_Hafta_${data.week}.pdf`}>
       {({ loading }) => (loading ? 'PDF Hazırlanıyor' : 'PDF İndir')}
   </PDFDownloadLink>
);

// PDF Export işlemi
export const handleExportPDF = async (data) => {
   if (!data?.orders?.length || !data.week) {
      console.error("Export edilecek veri eksik:", data);
      return;
   }

   const blob = await pdf(<PdfDocument data={data} />).toBlob();
   const link = document.createElement('a');
   link.href = URL.createObjectURL(blob);
   link.download = `Sevk_Plani_Hafta_${data.week}.pdf`;
   document.body.appendChild(link);
   link.click();
   document.body.removeChild(link);
};


// Excel Export işlemi
export const handleExportXLSX = (data) => {
   const groupedOrders = groupByDayOfWeek(data.orders);

   const wsData = [
       ['Gün', 'Statu', 'Sipariş No', 'Müşteri Adı', 'Sipariş Tarihi', 'Sevk Tarihi', 'Satıcı', 'Sevk Adresi', 'Sevk Notları'],
       ...Object.entries(groupedOrders).flatMap(([dayName, orders]) =>
           orders.map(order => [
               dayName,
               order.order_status || '',
               order.order_number || '',
               order.customer_name || '',
               formatDate(order.order_date),
               formatDate(order.shipment_date),
               order.sales_person || '',
               order.shipment_details || '',
               order.shipment_notes || ''
           ])
       )
   ];

   const wb = XLSX.utils.book_new();
   const ws = XLSX.utils.aoa_to_sheet(wsData);
   XLSX.utils.book_append_sheet(wb, ws, 'Sevk Plani');
   XLSX.writeFile(wb, 'Sevk_Plani.xlsx');
};

export default PdfExportButton;