// frontend/src/components/orderarchive/containers/OrderArchiveContainer.js
import React, { useState, useCallback } from 'react';
import OrderArchiveFilters from './OrderArchiveFilters';
import OrderArchiveTable from './OrderArchiveTable';
import useOrderArchive from '../hooks/useOrderArchive';
import '../css/OrderArchiveContainer.css';

const OrderArchiveContainer = () => {
    const {
        data,
        loading,
        error,
        totalItems,
        totalPages,
        currentPage,
        pageSize,
        handlePageChange,
        handlePageSizeChange,
        fetchData,
        searchData
    } = useOrderArchive();

    const [activeFilters, setActiveFilters] = useState({
        searchQuery: '',
        searchField: 'all',
        year: null
    });

    const handleFilterChange = useCallback(async (newFilters) => {
        setActiveFilters(prev => ({
            ...prev,
            ...newFilters
        }));

        try {
            if (newFilters.searchQuery) {
                await searchData(
                    newFilters.searchQuery,
                    newFilters.searchField || 'all',
                    currentPage,
                    pageSize
                );
            }
            else if (newFilters.year) {
                await fetchData({
                    year: newFilters.year,
                    page: currentPage,
                    pageSize
                });
            }
            else {
                setActiveFilters({
                    searchQuery: '',
                    searchField: 'all',
                    year: null
                });
            }
        } catch (error) {
            console.error('Veri yükleme hatası:', error);
        }
    }, [currentPage, pageSize, fetchData, searchData]);

    const handlePageChangeWithFilters = useCallback(async (newPage) => {
        try {
            if (activeFilters.searchQuery) {
                await searchData(
                    activeFilters.searchQuery,
                    activeFilters.searchField,
                    newPage,
                    pageSize
                );
            } else if (activeFilters.year) {
                await fetchData({
                    year: activeFilters.year,
                    page: newPage,
                    pageSize
                });
            }
            handlePageChange(newPage);
        } catch (error) {
            console.error('Sayfa değiştirme hatası:', error);
        }
    }, [activeFilters, pageSize, searchData, fetchData, handlePageChange]);

    const handlePageSizeChangeWithFilters = useCallback(async (newSize) => {
        try {
            if (activeFilters.searchQuery) {
                await searchData(
                    activeFilters.searchQuery,
                    activeFilters.searchField,
                    1,
                    newSize
                );
            } else if (activeFilters.year) {
                await fetchData({
                    year: activeFilters.year,
                    page: 1,
                    pageSize: newSize
                });
            }
            handlePageSizeChange(newSize);
        } catch (error) {
            console.error('Sayfa boyutu değiştirme hatası:', error);
        }
    }, [activeFilters, searchData, fetchData, handlePageSizeChange]);

    return (
        <div className="orderarchive-container">
            <div className="orderarchive-container__top">
                <h2 className="orderarchive-container__title">
                    Uyumsoft Arşiv Sipariş Detay 2005-2023
                </h2>
                <div className="orderarchive-container__filters">
                    <OrderArchiveFilters 
                        onFilterChange={handleFilterChange}
                        activeFilters={activeFilters}
                    />
                </div>
            </div>
            
            <div className="orderarchive-container__table">
                <OrderArchiveTable 
                    data={data}
                    loading={loading}
                    error={error}
                    totalItems={totalItems}
                    totalPages={totalPages}
                    currentPage={currentPage}
                    pageSize={pageSize}
                    onPageChange={handlePageChangeWithFilters}
                    onPageSizeChange={handlePageSizeChangeWithFilters}
                />
            </div>
        </div>
    );
};

export default OrderArchiveContainer;