// frontend/src/components/BomCostManager/utils/dailyRates.js

import {
  fetchDailyRatesFromBackend,
  fetchSingleRateFromBackend,
  fallbackRates
} from '../services/bcm_rateApi';

/**
 * Belirli bir para birimi için TRY bazlı kur değerini backend API'den getirir.
 * 
 * @param {string} currencyCode - Döviz kodu (örn: "USD", "EUR", "GBP", "TRY")
 * @returns {Promise<number|null>} - Döviz kuru (TRY bazlı)
 */
export async function getDailyRate(currencyCode) {
  if (currencyCode.toUpperCase() === "TRY") {
    return 1;
  }

  try {
    // Backend API'den kur bilgisini al
    const rate = await fetchSingleRateFromBackend(currencyCode);
    console.log(`${currencyCode} için kur: ${rate}`);
    return rate;
  } catch (error) {
    console.error("Döviz kurları alınırken hata oluştu:", error);
    // Hata durumunda sabit değerlere dön
    return fallbackRates[currencyCode.toUpperCase()] || null;
  }
}

/**
 * Tüm kurları tek seferde almak için kullanılabilir
 * @returns {Promise<Object|null>} - Tüm kurları içeren bir obje
 */
export async function getAllRates() {
  try {
    // Backend API'den tüm kurları al
    const rates = await fetchDailyRatesFromBackend();
    
    // Yanıtta TRY değeri olmasa bile eklenmesini sağla
    if (!rates.TRY) {
      rates.TRY = 1;
    }
    
    return rates;
  } catch (error) {
    console.error("Tüm kurlar alınırken hata oluştu:", error);
    return fallbackRates;
  }
}