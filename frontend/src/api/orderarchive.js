// frontend/src/api/orderarchive.js
import axiosInstance from './axiosconfig';

const OrderArchiveAPI = {
    search: async (query, field = 'all', page = 1, pageSize = 100) => {
        if (!query) {
            throw new Error('Arama metni boş olamaz.');
        }

        // İstek öncesi debug
        console.log('Arama isteği başlatılıyor:', {
            rawQuery: query,
            encodedQuery: encodeURIComponent(query),
            field,
            url: `/orderarchive/search/?q=${encodeURIComponent(query)}&fields=${field}&page=${page}&page_size=${pageSize}`
        });

        try {
            // Direct URL kullanımı
            const response = await axiosInstance.get(`/orderarchive/search/?q=${encodeURIComponent(query)}&fields=${field}&page=${page}&page_size=${pageSize}`);

            // Yanıt debug
            console.log('Backend yanıtı (raw):', response);
            console.log('Backend data:', response.data);
            console.log('Backend status:', response.status);
            console.log('Backend headers:', response.headers);

            // Yanıt kontrolü
            if (!response.data.results) {
                console.error('Yanıt formatı hatalı:', response.data);
                throw new Error('Sunucu yanıtı beklenen formatta değil');
            }

            // Success yanıtı
            console.log('İşlenmiş sonuçlar:', {
                totalItems: response.data.total_items,
                totalPages: response.data.total_pages,
                currentPage: response.data.current_page,
                resultCount: response.data.results.length,
                firstResult: response.data.results[0],
                lastResult: response.data.results[response.data.results.length - 1]
            });

            return response.data;
        } catch (error) {
            // Hata debug
            console.error('API Hatası:', {
                message: error.message,
                status: error.response?.status,
                statusText: error.response?.statusText,
                data: error.response?.data,
                config: {
                    url: error.config?.url,
                    method: error.config?.method,
                    params: error.config?.params,
                    headers: error.config?.headers
                }
            });
            throw error;
        }
    },

    filterByYear: async (year, page = 1, pageSize = 100) => {
        // Yıl filtresi yönetimi aynı kalabilir
        if (!year) {
            throw new Error('Yıl parametresi gereklidir.');
        }

        try {
            const response = await axiosInstance.get('/orderarchive/', {
                params: {
                    year,
                    page,
                    page_size: pageSize
                }
            });
            return response.data;
        } catch (error) {
            console.error('Yıl filtresi hatası:', error);
            throw error;
        }
    }
};

export default OrderArchiveAPI;