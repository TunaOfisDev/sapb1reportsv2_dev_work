// frontend/src/hooks/useOrderFilters.js
import { useState, useCallback } from 'react';
import OrderArchiveAPI from '../../../api/orderarchive';

const useOrderFilters = (onFilterChange) => {
    const [searchQuery, setSearchQuery] = useState('');
    const [searchError, setSearchError] = useState(null);
    const [isSearching, setIsSearching] = useState(false);

    const handleSearchQueryChange = useCallback((event) => {
        const newValue = event.target.value;
        console.log('Search query changed:', {
            oldValue: searchQuery,
            newValue,
            length: newValue.length
        });
        setSearchQuery(newValue);
        setSearchError(null);
    }, [searchQuery]);

    const handleSearch = useCallback(async (field = 'all') => {
        const query = searchQuery.trim();

        console.log('Search initiated:', {
            query,
            field,
            timestamp: new Date().toISOString()
        });

        if (!query) {
            setSearchError('Arama metni boş olamaz');
            return;
        }

        try {
            setIsSearching(true);
            setSearchError(null);

            console.log('Making API call:', {
                endpoint: '/orderarchive/search/',
                params: {
                    q: query,
                    fields: field  // Backend'e 'fields' olarak gönderiliyor
                }
            });

            const searchResults = await OrderArchiveAPI.search(query, field);

            console.log('Search results:', {
                totalItems: searchResults.total_items,
                totalPages: searchResults.total_pages,
                resultCount: searchResults.results?.length
            });

            if (typeof onFilterChange === 'function') {
                onFilterChange({
                    searchQuery: query,
                    searchField: field,
                    results: searchResults
                });
            }
        } catch (error) {
            console.error('Search error:', error);
            setSearchError(error.message || 'Arama sırasında bir hata oluştu');
        } finally {
            setIsSearching(false);
        }
    }, [searchQuery, onFilterChange]);

    return {
        searchQuery,
        searchError,
        isSearching,
        handleSearchQueryChange,
        handleSearch,
        resetFilters: useCallback(() => {
            setSearchQuery('');
            setSearchError(null);
            if (typeof onFilterChange === 'function') {
                onFilterChange({});
            }
        }, [onFilterChange])
    };
};

export default useOrderFilters;