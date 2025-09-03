// frontend/src/components/CustomerSalesV2/containers/CustomerSalesV2Container.js
import React, { useState, useMemo, useCallback } from 'react';
import { Button, message, Tag } from 'antd';
import { DownloadOutlined, SyncOutlined } from '@ant-design/icons';

import useCustomerSalesV2 from '../hooks/useCustomerSalesV2';
import CustomerSalesV2Table from './CustomerSalesV2Table';
import MultiFilterLine from '../utils/MultiFilterLine';
import { exportToXLSX } from '../utils/XLSXExport'; 

import '../css/CustomerSalesV2Container.css';

/**
 * Müşteri Satış Özeti V2 raporunun ana konteyner bileşeni.
 * Tüm alt bileşenleri (filtreler, tablo, butonlar) yönetir ve veri akışını organize eder.
 */
const CustomerSalesV2Container = () => {
  // 1. STATE YÖNETİMİ
  // Kullanıcının arayüzde seçtiği filtreleri tutan state
  const [filters, setFilters] = useState({
    satici: [],
    satis_tipi: [],
    cari_grup: [],
  });

  // 2. VERİ ÇEKME (CUSTOM HOOK)
  // useCustomerSalesV2 hook'u, API ile olan tüm iletişimi ve state'i yönetir.
  const {
    reportData,
    summaryData: grandTotalSummary, // Hook'tan gelen genel toplamı isimlendiriyoruz
    filterOptions,
    lastUpdated,
    isLoadingReport,
    isReportError,
    triggerSync,
    isSyncing,
  } = useCustomerSalesV2();

  // 3. FİLTRELEME MANTIĞI (CLIENT-SIDE)
  // Filtreler değiştiğinde veya ana veri geldiğinde, bu memoized fonksiyon çalışır
  // ve veriyi frontend tarafında filtreler.
  const filteredData = useMemo(() => {
    // Eğer hiç filtre seçilmemişse, tüm veriyi döndür
    const hasActiveFilters = Object.values(filters).some(f => f.length > 0);
    if (!hasActiveFilters) {
      return reportData;
    }

    return reportData.filter(row => {
      const saticiMatch = filters.satici.length === 0 || filters.satici.includes(row.satici);
      const satisTipiMatch = filters.satis_tipi.length === 0 || filters.satis_tipi.includes(row.satis_tipi);
      const cariGrupMatch = filters.cari_grup.length === 0 || filters.cari_grup.includes(row.cari_grup);
      return saticiMatch && satisTipiMatch && cariGrupMatch;
    });
  }, [reportData, filters]);

  // Filtreler değiştiğinde, sadece filtrelenmiş veriye ait alt toplamları hesapla
  const dynamicSummary = useMemo(() => {
    // Eğer filtre yoksa, hook'tan gelen genel toplamı kullan
    const hasActiveFilters = Object.values(filters).some(f => f.length > 0);
    if (!hasActiveFilters) {
        return grandTotalSummary;
    }
    
    // Filtre varsa, filtrelenmiş veriye göre yeniden hesapla
    const initialSummary = {
        ToplamNetSPB_EUR: 0, Ocak: 0, Şubat: 0, Mart: 0, Nisan: 0, Mayıs: 0, Haziran: 0,
        Temmuz: 0, Ağustos: 0, Eylül: 0, Ekim: 0, Kasım: 0, Aralık: 0
    };
    
    return filteredData.reduce((acc, row) => {
        acc.ToplamNetSPB_EUR += parseFloat(row.toplam_net_spb_eur || 0);
        acc.Ocak += parseFloat(row.ocak || 0);
        acc.Şubat += parseFloat(row.subat || 0);
        acc.Mart += parseFloat(row.mart || 0);
        // ... diğer aylar
        acc.Aralık += parseFloat(row.aralik || 0);
        return acc;
    }, initialSummary);

  }, [filteredData, grandTotalSummary, filters]);


  // Filtre bileşeninden gelen değişikliği state'e yansıtan callback fonksiyonu
  const handleFilterChange = useCallback((filterKey, values) => {
    setFilters(prevFilters => ({
      ...prevFilters,
      [filterKey]: values,
    }));
  }, []);
  
  // Excel'e aktarma fonksiyonu
  const handleExport = () => {
      if (filteredData.length > 0) {
        // 1. Anlık tarih ve saat bilgisini alıp formatlıyoruz.
        const now = new Date();
        const timestamp = `${now.getFullYear()}-${(now.getMonth() + 1).toString().padStart(2, '0')}-${now.getDate().toString().padStart(2, '0')}_${now.getHours().toString().padStart(2, '0')}-${now.getMinutes().toString().padStart(2, '0')}`;
        
        // 2. Dinamik ve uzantılı dosya adını oluşturuyoruz.
        const fileName = `MusteriSatisOzeti_${timestamp}.xlsx`;
  
        // 3. Dışa aktarma fonksiyonunu yeni dosya adıyla çağırıyoruz.
        exportToXLSX(filteredData, fileName, 'Müşteri Satış Özeti');
        
        message.success('Veriler başarıyla Excel\'e aktarıldı!');
      } else {
        message.warning('Dışa aktarılacak veri bulunamadı.');
      }
    };


  return (
    <div className="customer-sales-container">
      <div className="customer-sales-container__header">
        <h1 className="customer-sales-container__title">Müşteri Bazlı Satış Özeti (EUR)</h1>
        <div className="customer-sales-container__button-wrapper">
          <Tag color="blue" style={{ display: 'flex', alignItems: 'center' }}>
            Son Güncelleme: {isLoadingReport ? '...' : lastUpdated}
          </Tag>
          <Button
            type="primary"
            icon={<SyncOutlined />}
            loading={isSyncing}
            onClick={triggerSync}
            className="customer-sales-container__button"
          >
            HANA Veri Çek
          </Button>
          <Button
            icon={<DownloadOutlined />}
            onClick={handleExport}
            className="customer-sales-container__button"
          >
            Excel'e Aktar
          </Button>
        </div>
      </div>

      <MultiFilterLine
        filterOptions={filterOptions}
        filters={filters}
        onFilterChange={handleFilterChange}
      />
      
      <CustomerSalesV2Table
        data={filteredData}
        summaryData={dynamicSummary}
        isLoading={isLoadingReport}
        isError={isReportError}
      />
    </div>
  );
};

export default CustomerSalesV2Container;