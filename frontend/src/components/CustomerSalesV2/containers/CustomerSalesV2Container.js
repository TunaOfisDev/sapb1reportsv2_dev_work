// frontend/src/components/CustomerSalesV2/containers/CustomerSalesV2Container.js
import React, { useState, useMemo, useCallback } from 'react';
import { Button, message, Tag } from 'antd';
import { DownloadOutlined, SyncOutlined } from '@ant-design/icons';

import useCustomerSalesV2 from '../hooks/useCustomerSalesV2';
import CustomerSalesV2Table from './CustomerSalesV2Table';
import MultiFilterLine from '../utils/MultiFilterLine';
import { exportToXLSX } from '../utils/XLSXExport'; 

import '../css/CustomerSalesV2Container.css';

const CustomerSalesV2Container = () => {
  // 1. STATE YÖNETİMİ
  const [filters, setFilters] = useState({
    satici: [],
    satis_tipi: [],
    cari_grup: [],
  });

  // DÜZELTME: EKSİK OLAN STATE TANIMI BURAYA EKLENDİ
  const [globalFilter, setGlobalFilter] = useState('');

  // 2. VERİ ÇEKME (CUSTOM HOOK)
  const {
    reportData,
    summaryData: grandTotalSummary,
    filterOptions,
    lastUpdated,
    isLoadingReport,
    isReportError,
    triggerSync,
    isSyncing,
  } = useCustomerSalesV2();

  // YENİ: Genel arama state'ini güncelleyen fonksiyon
  const handleGlobalFilterChange = useCallback((value) => {
    setGlobalFilter(value || ''); // Değer null veya undefined ise boş string ata
  }, []);

  // Filtre bileşeninden gelen değişikliği state'e yansıtan callback fonksiyonu
  const handleFilterChange = useCallback((filterKey, values) => {
    setFilters(prevFilters => ({
      ...prevFilters,
      [filterKey]: values,
    }));
  }, []);

  // 3. FİLTRELEME MANTIĞI (CLIENT-SIDE)
  const filteredData = useMemo(() => {
    let data = reportData;

    const hasActiveSelectFilters = Object.values(filters).some(f => f.length > 0);
    if (hasActiveSelectFilters) {
      data = data.filter(row => {
        const saticiMatch = filters.satici.length === 0 || filters.satici.includes(row.satici);
        const satisTipiMatch = filters.satis_tipi.length === 0 || filters.satis_tipi.includes(row.satis_tipi);
        const cariGrupMatch = filters.cari_grup.length === 0 || filters.cari_grup.includes(row.cari_grup);
        return saticiMatch && satisTipiMatch && cariGrupMatch;
      });
    }

    if (globalFilter) {
      const lowerCaseFilter = globalFilter.toLowerCase();
      data = data.filter(row => {
        return (
          row.musteri_adi.toLowerCase().includes(lowerCaseFilter) ||
          row.musteri_kodu.toLowerCase().includes(lowerCaseFilter)
        );
      });
    }

    return data;
  }, [reportData, filters, globalFilter]);

  const dynamicSummary = useMemo(() => {
    const hasActiveFilters = Object.values(filters).some(f => f.length > 0) || globalFilter;
    if (!hasActiveFilters) {
        return grandTotalSummary;
    }
    
    const initialSummary = {
        ToplamNetSPB_EUR: 0, Ocak: 0, Şubat: 0, Mart: 0, Nisan: 0, Mayıs: 0, Haziran: 0,
        Temmuz: 0, Ağustos: 0, Eylül: 0, Ekim: 0, Kasım: 0, Aralık: 0
    };
    
    return filteredData.reduce((acc, row) => {
        acc.ToplamNetSPB_EUR += parseFloat(row.toplam_net_spb_eur || 0);
        acc.Ocak += parseFloat(row.ocak || 0);
        acc.Şubat += parseFloat(row.subat || 0);
        acc.Mart += parseFloat(row.mart || 0);
        acc.Nisan += parseFloat(row.nisan || 0);
        acc.Mayıs += parseFloat(row.mayis || 0);
        acc.Haziran += parseFloat(row.haziran || 0);
        acc.Temmuz += parseFloat(row.temmuz || 0);
        acc.Ağustos += parseFloat(row.agustos || 0);
        acc.Eylül += parseFloat(row.eylul || 0);
        acc.Ekim += parseFloat(row.ekim || 0);
        acc.Kasım += parseFloat(row.kasim || 0);
        acc.Aralık += parseFloat(row.aralik || 0);

        return acc;
    }, initialSummary);

  }, [filteredData, grandTotalSummary, filters, globalFilter]);

  const handleExport = () => {
      if (filteredData.length > 0) {
        const now = new Date();
        const timestamp = `${now.getFullYear()}-${(now.getMonth() + 1).toString().padStart(2, '0')}-${now.getDate().toString().padStart(2, '0')}_${now.getHours().toString().padStart(2, '0')}-${now.getMinutes().toString().padStart(2, '0')}`;
        const fileName = `MusteriSatisOzeti_${timestamp}.xlsx`;
        exportToXLSX(filteredData, fileName, 'Müşteri Satış Özeti');
        message.success('Veriler başarıyla Excel\'e aktarıldı!');
      } else {
        message.warning('Dışa aktarılacak veri bulunamadı.');
      }
    };

  return (
    <div className="customer-sales-container">
      <div className="customer-sales-container__header">
        <h1 className="customer-sales-container__title">Müşteri Satış Sipariş Özeti(EUR)-Satış Tipi Bazında</h1>
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
        globalFilter={globalFilter}
        onGlobalFilterChange={handleGlobalFilterChange}
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