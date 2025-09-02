import React from 'react';
import PropTypes from 'prop-types';
import { Select } from 'antd';
import '../css/MultiFilterLine.css';

/**
 * Rapor için çoklu seçim yapılabilen filtre satırını oluşturan bileşen.
 * Ant Design'ın Select bileşenini kullanarak arama ve çoklu seçim özellikleri sunar.
 *
 * @param {object} props - Bileşenin propları.
 * @param {object} props.filterOptions - Filtre kutularını dolduracak seçenekleri içeren nesne.
 * @param {string[]} props.filterOptions.saticilar - Satıcı listesi.
 * @param {string[]} props.filterOptions.satisTipleri - Satış Tipi listesi.
 * @param {string[]} props.filterOptions.cariGruplar - Cari Grup listesi.
 * @param {object} props.filters - Anlık olarak seçili olan filtre değerlerini tutan nesne.
 * @param {function} props.onFilterChange - Bir filtrede değişiklik olduğunda çağrılacak olan ana fonksiyon.
 */
const MultiFilterLine = ({ filterOptions, filters, onFilterChange }) => {
  // Bir filtre değiştiğinde, ana bileşendeki state'i güncellemek için bu fonksiyon çağrılır.
  const handleFilterChange = (filterKey, selectedValues) => {
    onFilterChange(filterKey, selectedValues);
  };

  /**
   * Ant Design Select bileşeni için seçenek listesini formatlar.
   * @param {string[]} optionsArray - String dizisi olarak gelen seçenekler.
   * @returns {object[]} Ant Design'e uygun formatta { label, value } nesnelerinden oluşan dizi.
   */
  const formatOptions = (optionsArray = []) =>
    optionsArray.map((option) => ({
      label: option,
      value: option,
    }));

  return (
    <div className="multi-filter-line">
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
          maxTagCount="responsive" // Çok fazla seçim olduğunda etiketleri gizler
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

// Bileşenin alması gereken propların tiplerini ve zorunluluklarını belirliyoruz.
// Bu, kodun daha güvenli ve anlaşılır olmasını sağlar.
MultiFilterLine.propTypes = {
  filterOptions: PropTypes.shape({
    saticilar: PropTypes.arrayOf(PropTypes.string),
    satisTipleri: PropTypes.arrayOf(PropTypes.string),
    cariGruplar: PropTypes.arrayOf(PropTypes.string),
  }).isRequired,
  filters: PropTypes.object.isRequired,
  onFilterChange: PropTypes.func.isRequired,
};

export default MultiFilterLine;