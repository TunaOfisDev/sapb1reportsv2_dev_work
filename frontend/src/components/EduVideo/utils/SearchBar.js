// frontend/src/components/EduVideo/utils/SearchBar.js
import React, { useState } from 'react';
import '../css/SearchBar.css';

const SearchBar = ({ onSearch }) => {
  const [searchTerm, setSearchTerm] = useState('');

  const handleSearchChange = (e) => {
    setSearchTerm(e.target.value);
  };

  const handleSearch = () => {
    // Arama terimindeki Türkçe karakterleri İngilizce karşılıklarıyla değiştirin
    const normalizedSearchTerm = normalizeTurkishCharacters(searchTerm);
    onSearch(normalizedSearchTerm);
  };

  // Türkçe karakterleri İngilizce karşılıklarıyla değiştiren işlev
  const normalizeTurkishCharacters = (text) => {
    return text
      .replace(/ı/g, 'i')
      .replace(/ç/g, 'c')
      .replace(/ğ/g, 'g')
      .replace(/ü/g, 'u')
      .replace(/ş/g, 's')
      .replace(/ö/g, 'o')
      .replace(/İ/g, 'I')
      .replace(/Ç/g, 'C')
      .replace(/Ğ/g, 'G')
      .replace(/Ü/g, 'U')
      .replace(/Ş/g, 'S')
      .replace(/Ö/g, 'O');
  };

  return (
    <div className="search-bar-edu">
      <input
        type="text"
        placeholder="Başlık veya açıklama ara..."
        value={searchTerm}
        onChange={handleSearchChange}
      />
      <button onClick={handleSearch}>Ara</button>
    </div>
  );
};

export default SearchBar;