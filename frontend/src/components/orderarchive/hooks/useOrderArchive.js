// frontend/src/hooks/useOrderArchive.js
import { useState, useCallback } from 'react';
import OrderArchiveAPI from '../../../api/orderarchive';

const useOrderArchive = () => {
    const [data, setData] = useState([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const [totalItems, setTotalItems] = useState(0);
    const [totalPages, setTotalPages] = useState(0);
    const [currentPage, setCurrentPage] = useState(1);
    const [pageSize, setPageSize] = useState(100);

    const handleResponse = useCallback((response) => {
        setData(response.results || []);
        setTotalItems(response.total_items || 0);
        setTotalPages(response.total_pages || 0);
        setCurrentPage(response.current_page || 1);
    }, []);

    const fetchData = useCallback(async ({ year, page = 1, pageSize = 100 }) => {
        if (!year) return;

        setLoading(true);
        setError(null);

        try {
            const response = await OrderArchiveAPI.filterByYear(year, page, pageSize);
            handleResponse(response);
        } catch (err) {
            setError(err.message || 'Veri yükleme hatası');
            console.error('Veri yükleme hatası:', err);
            setData([]);
        } finally {
            setLoading(false);
        }
    }, [handleResponse]);

    const searchData = useCallback(async (query, field = 'all', page = 1, pageSize = 100) => {
        if (!query) return;

        setLoading(true);
        setError(null);

        try {
            const response = await OrderArchiveAPI.search(query, field, page, pageSize);
            handleResponse(response);
        } catch (err) {
            setError(err.message || 'Arama hatası');
            console.error('Arama hatası:', err);
            setData([]);
        } finally {
            setLoading(false);
        }
    }, [handleResponse]);

    const handlePageChange = useCallback((newPage) => {
        setCurrentPage(newPage);
    }, []);

    const handlePageSizeChange = useCallback((newSize) => {
        setPageSize(newSize);
        setCurrentPage(1);
    }, []);

    return {
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
    };
};

export default useOrderArchive;