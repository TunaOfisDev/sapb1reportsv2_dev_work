// frontend/src/components/OpenOrderDocSum/utils/DateColumnFilter.js
import React, { useState } from 'react';
import '../css/SalesOrderDocSumTable.css';

// Bu fonksiyon kullanıcı girdisini YYYY-MM-DD formatına dönüştürür
const formatDateForBackend = (dateString) => {
  const parts = dateString.split('.');
  return `${parts[2]}-${parts[1]}-${parts[0]}`; // DD.MM.YYYY -> YYYY-MM-DD
};

const DateColumnFilter = ({ column }) => {
  const { filterValue, setFilter } = column;
  const [inputValue, setInputValue] = useState('');

  // Kullanıcı input değerini güncellediğinde çalışacak fonksiyon
  const handleInputChange = (e) => {
    const value = e.target.value;
    setInputValue(value);
    if (value.length === 10) { // DD.MM.YYYY formatında 10 karakter olmalı
      const formattedDate = formatDateForBackend(value);
      setFilter(formattedDate);
    } else {
      setFilter(undefined); // Filtreyi kaldır
    }
  };

  // Sıralama işlemi tetiklenmesin diye click event'ini engelleyelim
  const handleClick = (e) => {
    e.stopPropagation(); // Bu satır, event'in üst elementlere taşınmasını önler
  };

  return (
    <div className="open-order-doc-sum__filter" > 
    <input
      value={inputValue}
      onChange={handleInputChange}
      onClick={handleClick}
      className="open-order-doc-sum__filter-input"
      placeholder='GG.AA.YYYY'
    />
    </div>
  );
};

export default DateColumnFilter;