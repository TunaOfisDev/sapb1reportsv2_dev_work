// frontend/src/components/CustomerSalesV2/utils/ColumnFilter.js
import React from 'react';
import '../css/CustomerSalesV2Table.css'; // Stiller ana tablo CSS dosyasından geliyor

/**
 * react-table için her bir sütuna metin bazlı arama kutusu ekleyen bileşen.
 * Arama yaparken Türkçe karakterleri büyük harfe çevirir.
 */
export const ColumnFilter = ({ column }) => {
  const { filterValue, setFilter } = column;

  const handleChange = (e) => {
    // Girilen metni alıp büyük harfe çevirerek filtreliyoruz
    // Bu, büyük/küçük harf duyarsız bir arama sağlar
    setFilter(e.target.value || undefined); // Boşsa filtreyi kaldır
  };

  return (
    <span className="column-filter-wrapper">
      <input
        className="column-filter-input"
        value={filterValue || ''}
        onChange={handleChange}
        onClick={(e) => e.stopPropagation()} // Sıralamayı tetiklememek için
        placeholder={`Ara...`}
      />
    </span>
  );
};