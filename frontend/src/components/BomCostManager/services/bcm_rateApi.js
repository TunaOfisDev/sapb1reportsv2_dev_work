// frontend/src/components/BomCostManager/services/bcm_rateApi.js

import axiosInstance from '../../../api/axiosconfig';

const BASE_URL = '/bomcostmanager';

/**
 * Backend üzerinden döviz kurlarını getirir.
 * Bu yaklaşım CORS sorunlarını önlemek için tercih edilir.
 * 
 * @returns {Promise<Object>} - TRY bazlı döviz kurları objesi. Örnek: {USD: 30.5, EUR: 33.2, GBP: 38.7, TRY: 1}
 */
export const fetchDailyRatesFromBackend = async () => {
  try {
    const response = await axiosInstance.get(`${BASE_URL}/exchange-rates/`);
    return response.data;
  } catch (error) {
    console.error('Döviz kurları backend üzerinden alınırken hata oluştu:', error);
    throw error;
  }
};

/**
 * Belirli bir para birimi için TRY bazlı kur değerini backend üzerinden getirir.
 * 
 * @param {string} currencyCode - Döviz kodu (örn: "USD", "EUR", "GBP")
 * @returns {Promise<number>} - TRY bazlı döviz kuru
 */
export const fetchSingleRateFromBackend = async (currencyCode) => {
  try {
    const response = await axiosInstance.get(`${BASE_URL}/exchange-rates/${currencyCode}/`);
    return response.data.rate;
  } catch (error) {
    console.error(`${currencyCode} için döviz kuru backend üzerinden alınırken hata oluştu:`, error);
    throw error;
  }
};

/**
 * Varsayılan döviz kurları. API çağrısı başarısız olursa kullanılacak.
 */
export const fallbackRates = {
  USD: -30.5,  // TRY bazlı örnek değerler (1 USD = 30.5 TRY)
  EUR: -33.2,
  GBP: -38.7,
  TRY: 1
};

/**
 * Belirli bir para birimi için TRY bazlı kur değerini döndürür.
 * Önce backend endpoint'i denenir, başarısız olursa fallback değerleri kullanılır.
 * 
 * @param {string} currencyCode - Döviz kodu (örn: "USD", "EUR", "GBP", "TRY")
 * @returns {Promise<number>} - TRY bazlı döviz kuru
 */
export const getDailyRate = async (currencyCode) => {
  // TRY için direkt 1 döndür
  if (currencyCode.toUpperCase() === "TRY") {
    return 1;
  }

  try {
    // Önce backend üzerinden dene
    const rate = await fetchSingleRateFromBackend(currencyCode);
    return rate;
  } catch (error) {
    console.warn(`${currencyCode} için backend üzerinden kur alınamadı, fallback değerleri kullanılıyor.`);
    
    // Fallback değerleri kullan
    return fallbackRates[currencyCode.toUpperCase()] || null;
  }
};

/**
 * Tüm döviz kurlarını tek seferde getirir.
 * Önce backend endpoint'i denenir, başarısız olursa fallback değerleri kullanılır.
 * 
 * @returns {Promise<Object>} - TRY bazlı tüm döviz kurlarını içeren obje
 */
export const getAllRates = async () => {
  try {
    // Önce backend üzerinden dene
    const rates = await fetchDailyRatesFromBackend();
    return rates;
  } catch (error) {
    console.warn('Döviz kurları backend üzerinden alınamadı, fallback değerleri kullanılıyor.');
    
    // Fallback değerleri kullan
    return fallbackRates;
  }
};