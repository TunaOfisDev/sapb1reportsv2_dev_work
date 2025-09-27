// frontend/src/components/orderarchive/containers/OrderArchiveFilters.js
import React, { useState, useCallback } from 'react';
import { YEARS } from '../utils/constants';
import useOrderFilters from '../hooks/useOrderFilters';
import '../css/OrderArchiveFilters.css';

const OrderArchiveFilters = ({ onFilterChange }) => {
    const [selectedYear, setSelectedYear] = useState('');
    const [selectedSearchField, setSelectedSearchField] = useState('all');

    const {
        searchQuery,
        searchError,
        isSearching,
        handleSearchQueryChange,
        handleSearch,
        resetFilters,
    } = useOrderFilters(onFilterChange);

    // Arama alanları tanımlaması
    const searchFields = [
        { value: 'all', label: 'Tüm Alanlarda Ara' },
        { value: 'country', label: 'Ülke' },
        { value: 'city', label: 'Şehir' },
        { value: 'order_number', label: 'Sipariş No' },
        { value: 'customer_code', label: 'Müşteri Kodu' },
        { value: 'customer_name', label: 'Müşteri Adı' },
        { value: 'item_code', label: 'Ürün Kodu' },
        { value: 'item_description', label: 'Ürün Açıklaması' },
        { value: 'document_description', label: 'Belge Açıklaması' },
        { value: 'seller', label: 'Satıcı' }
    ];

    // Yıl değişikliğini handle et
    const handleYearChange = useCallback((event) => {
        const value = event.target.value;
        setSelectedYear(value);
        if (value) {
            onFilterChange({ year: value });
            handleSearchQueryChange({ target: { value: '' } });
            setSelectedSearchField('all');
        } else {
            onFilterChange({});
        }
    }, [onFilterChange, handleSearchQueryChange]);

    // Arama alanı değişikliğini handle et
    const handleSearchFieldChange = useCallback((event) => {
        const newField = event.target.value;
        setSelectedSearchField(newField);
        
        if (selectedYear) {
            setSelectedYear('');
            onFilterChange({});
        }
        handleSearchQueryChange({ target: { value: '' } });
    }, [selectedYear, onFilterChange, handleSearchQueryChange]);

    // Aramayı gerçekleştir
    const handleSearchClick = useCallback(() => {
        if (!searchQuery.trim()) return;
        handleSearch(selectedSearchField);
    }, [searchQuery, selectedSearchField, handleSearch]);

    // Enter tuşuna basıldığında arama yap
    const handleKeyPress = useCallback((event) => {
        if (event.key === 'Enter' && searchQuery.trim()) {
            handleSearch(selectedSearchField);
        }
    }, [searchQuery, selectedSearchField, handleSearch]);

    // Aramayı temizle
    const handleClearSearch = useCallback(() => {
        handleSearchQueryChange({ target: { value: '' } });
        setSelectedSearchField('all');
        onFilterChange({});
    }, [handleSearchQueryChange, onFilterChange]);

    // Tüm filtreleri temizle
    const handleResetAll = useCallback(() => {
        resetFilters();
        setSelectedYear('');
        setSelectedSearchField('all');
        handleSearchQueryChange({ target: { value: '' } });
        onFilterChange({});
    }, [resetFilters, handleSearchQueryChange, onFilterChange]);

    return (
        <div className="orderarchive-filters">
            {/* Yıl Filtresi */}
            <div className="orderarchive-filters__group">
                <div className="orderarchive-filters__field-select">
                    <label className="orderarchive-filters__label">Yıl Filtresi:</label>
                    <select
                        value={selectedYear}
                        onChange={handleYearChange}
                        className="orderarchive-filters__select"
                        disabled={searchQuery ? true : false}
                    >
                        <option value="">Yıl Seçiniz</option>
                        {YEARS.map(year => (
                            <option key={year} value={year}>{year}</option>
                        ))}
                    </select>
                    {selectedYear && (
                        <button
                            className="orderarchive-filters__button-clear"
                            onClick={() => handleYearChange({ target: { value: '' } })}
                            title="Yıl filtresini temizle"
                        >
                            ✕
                        </button>
                    )}
                </div>
            </div>

            {/* Arama Filtresi */}
            <div className="orderarchive-filters__group">
                <div className="orderarchive-filters__field-select">
                    <label className="orderarchive-filters__label">Arama Tipi:</label>
                    <select
                        value={selectedSearchField}
                        onChange={handleSearchFieldChange}
                        className="orderarchive-filters__select"
                        disabled={selectedYear ? true : false}
                    >
                        {searchFields.map(field => (
                            <option key={field.value} value={field.value}>
                                {field.label}
                            </option>
                        ))}
                    </select>
                </div>

                <div className="orderarchive-filters__search-input">
                    <label className="orderarchive-filters__label">Arama:</label>
                    <input
                        type="text"
                        className="orderarchive-filters__input"
                        placeholder={`${selectedSearchField === 'all' 
                            ? 'Tüm alanlarda ara...' 
                            : `${searchFields.find(f => f.value === selectedSearchField)?.label} ile ara...`}`}
                        value={searchQuery}
                        onChange={handleSearchQueryChange}
                        onKeyPress={handleKeyPress}
                        disabled={selectedYear ? true : false}
                    />
                </div>

                <div className="orderarchive-filters__buttons">
                    <button
                        className={`orderarchive-filters__button ${isSearching ? 'disabled' : ''}`}
                        onClick={handleSearchClick}
                        disabled={isSearching || selectedYear || !searchQuery.trim()}
                    >
                        {isSearching ? 'Aranıyor...' : 'Ara'}
                    </button>

                    {searchQuery && (
                        <button
                            className="orderarchive-filters__button-clear"
                            onClick={handleClearSearch}
                            title="Aramayı temizle"
                        >
                            ✕
                        </button>
                    )}
                </div>
            </div>

            {/* Filtreleri Temizle */}
            {(selectedYear || searchQuery) && (
                <button
                    className="orderarchive-filters__button-reset"
                    onClick={handleResetAll}
                    title="Tüm filtreleri temizle"
                >
                    Filtreleri Temizle
                </button>
            )}

            {/* Hata Mesajı */}
            {searchError && (
                <div className="orderarchive-filters__error">
                    {searchError}
                </div>
            )}
        </div>
    );
};

OrderArchiveFilters.defaultProps = {
    onFilterChange: () => {},
};

export default React.memo(OrderArchiveFilters);