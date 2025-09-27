// frontend/src/components/SalesOfferDocSum/utils/DateColumnFilter.js
import React, { useState, useEffect } from 'react';
import '../css/SalesOfferDocSumTable.css';

// Bu fonksiyon kullanıcı girdisini YYYY-MM-DD formatına dönüştürür
const formatDateForBackend = (dateString) => {
  const parts = dateString.split('.');
  return `${parts[2]}-${parts[1]}-${parts[0]}`; // DD.MM.YYYY -> YYYY-MM-DD
};

const DateColumnFilter = ({ column }) => {
  const { filterValue, setFilter } = column;
  const [inputValue, setInputValue] = useState(filterValue || ''); // Başlangıç değeri olarak filterValue ya da boş string

  // Kullanıcı input değerini güncellediğinde çalışacak fonksiyon
  const handleInputChange = (e) => {
    const value = e.target.value;
    setInputValue(value);
    if (value.length === 10) { // DD.MM.YYYY formatında 10 karakter olmalı
      const formattedDate = formatDateForBackend(value);
      setFilter(formattedDate); // Backend için uygun formata çevirip filtreyi ayarlıyoruz
    } else {
      setFilter(undefined); // Eğer format yanlışsa, filtreyi kaldır
    }
  };

  // Sıralama işlemi tetiklenmesin diye click event'ini engelleyelim
  const handleClick = (e) => {
    e.stopPropagation(); // Bu satır, event'in üst elementlere taşınmasını önler
  };

  // `filterValue` değiştiğinde `inputValue`'yu güncelle
  useEffect(() => {
    if (filterValue) {
      setInputValue(filterValue.split('-').reverse().join('.')); // YYYY-MM-DD -> DD.MM.YYYY
    } else {
      setInputValue(''); // Filtre yoksa input alanı boş bırakılır
    }
  }, [filterValue]);

  return (
    <div className="sales-offer-doc-sum__filter">
      <input
        value={inputValue}
        onChange={handleInputChange}
        onClick={handleClick}
        className="sales-offer-doc-sum__filter-input"
        placeholder="GG.AA.YYYY"
      />
    </div>
  );
};

export default DateColumnFilter;
