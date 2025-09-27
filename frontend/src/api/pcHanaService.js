// frontend/src/api/pcHanaService.js
import axiosInstance from './axiosconfig';
import tokenService from '../auth/tokenService';

const pcHanaService = {
    // Varyant için HANA DB verilerini güncelleme
    updateHanaData: async (variantId) => {
        try {
            // Token kontrolü
            const token = tokenService.getLocalAccessToken();
            if (!token) {
                throw new Error('Yetkilendirme tokeni bulunamadı');
            }

            // Variant ID kontrolü
            if (!variantId) {
                throw new Error('Variant ID bulunamadı');
            }

            const response = await axiosInstance.post(
                `productconfig/variants/${variantId}/update-hana-data/`,
                {}, // Boş request body
                {
                    headers: {
                        'Authorization': `Bearer ${token}`
                    }
                }
            );
            
            console.log('HANA Data Update Response:', response.data);
            
            if (response.data && response.data.message) {
                return {
                    success: true,
                    data: response.data,
                    message: response.data.message
                };
            }

            return {
                success: true,
                data: response.data
            };

        } catch (error) {
            console.error('HANA veri güncelleme hatası:', error);
            
            // Hata mesajını daha detaylı oluştur
            const errorMessage = error.response?.data?.detail || 
                               error.message || 
                               'HANA verileri güncellenirken bir hata oluştu';

            return {
                success: false,
                error: errorMessage
            };
        }
    },

    // HANA verilerini içeren varyant detaylarını getirme
    getVariantHanaDetails: async (variantId) => {
        try {
            // Token kontrolü
            const token = tokenService.getLocalAccessToken();
            if (!token) {
                throw new Error('Yetkilendirme tokeni bulunamadı');
            }

            // Variant ID kontrolü
            if (!variantId) {
                throw new Error('Variant ID bulunamadı');
            }

            const response = await axiosInstance.get(
                `productconfig/variants/${variantId}/details/`,
                {
                    headers: {
                        'Authorization': `Bearer ${token}`
                    }
                }
            );
            
            // HANA ile ilgili alanları seç
            const hanaDetails = {
                sap_item_code: response.data.sap_item_code || '',
                sap_item_description: response.data.sap_item_description || '',
                sap_U_eski_bilesen_kod: response.data.sap_U_eski_bilesen_kod || '',
                sap_price: response.data.sap_price || '0',
                sap_currency: response.data.sap_currency || 'EUR'
            };

            // Yanıt kontrolü
            if (!response.data) {
                throw new Error('Veri alınamadı');
            }

            return {
                success: true,
                data: hanaDetails
            };

        } catch (error) {
            console.error('HANA detayları getirme hatası:', error);
            
            // Hata mesajını daha detaylı oluştur
            const errorMessage = error.response?.data?.detail || 
                               error.message || 
                               'HANA detayları alınırken bir hata oluştu';

            return {
                success: false,
                error: errorMessage
            };
        }
    }
};

export default pcHanaService;