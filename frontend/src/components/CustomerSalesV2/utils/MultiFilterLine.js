// frontend/src/components/CustomerSalesV2/utils/MultiFilterLine.js
import React from 'react';
import PropTypes from 'prop-types';
import { Select, Input } from 'antd'; // Input bileşenini antd'den import ediyoruz
import { SearchOutlined } from '@ant-design/icons'; // Arama ikonu
import '../css/MultiFilterLine.css';

const MultiFilterLine = ({ filterOptions, filters, onFilterChange, globalFilter, onGlobalFilterChange }) => {
  const handleFilterChange = (filterKey, selectedValues) => {
    onFilterChange(filterKey, selectedValues);
  };

  const formatOptions = (optionsArray = []) =>
    optionsArray.map((option) => ({ label: option, value: option }));

  return (
    <div className="multi-filter-line">
      {/* YENİ: Genel Arama Kutusu */}
      <div className="filter-item global-search">
        <Input
          placeholder="Tüm Metinlerde Ara (Müşteri Adı, Kodu...)"
          prefix={<SearchOutlined />}
          value={globalFilter}
          onChange={(e) => onGlobalFilterChange(e.target.value)}
          allowClear
        />
      </div>

      {/* Satıcı Filtresi */}
      <div className="filter-item">
        <Select
          mode="multiple"
          allowClear
          style={{ width: '100%' }}
          placeholder="Satıcıya Göre Filtrele"
          value={filters.satici || []}
          onChange={(values) => handleFilterChange('satici', values)}
          options={formatOptions(filterOptions.saticilar)}
          maxTagCount="responsive"
        />
      </div>

      {/* Satış Tipi Filtresi */}
      <div className="filter-item">
        <Select
          mode="multiple"
          allowClear
          style={{ width: '100%' }}
          placeholder="Satış Tipine Göre Filtrele"
          value={filters.satis_tipi || []}
          onChange={(values) => handleFilterChange('satis_tipi', values)}
          options={formatOptions(filterOptions.satisTipleri)}
          maxTagCount="responsive"
        />
      </div>

      {/* Cari Grup Filtresi */}
      <div className="filter-item">
        <Select
          mode="multiple"
          allowClear
          style={{ width: '100%' }}
          placeholder="Cari Gruba Göre Filtrele"
          value={filters.cari_grup || []}
          onChange={(values) => handleFilterChange('cari_grup', values)}
          options={formatOptions(filterOptions.cariGruplar)}
          maxTagCount="responsive"
        />
      </div>
    </div>
  );
};

// Yeni propları PropTypes'a ekliyoruz
MultiFilterLine.propTypes = {
  filterOptions: PropTypes.shape({
    saticilar: PropTypes.arrayOf(PropTypes.string),
    satisTipleri: PropTypes.arrayOf(PropTypes.string),
    cariGruplar: PropTypes.arrayOf(PropTypes.string),
  }).isRequired,
  filters: PropTypes.object.isRequired,
  onFilterChange: PropTypes.func.isRequired,
  globalFilter: PropTypes.string.isRequired,
  onGlobalFilterChange: PropTypes.func.isRequired,
};

export default MultiFilterLine;