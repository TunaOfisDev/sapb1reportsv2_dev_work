// frontend/src/components/BomCostManager/utils/masterCostButton.js

import { getMaxPositiveLevel } from './getMaxPositiveLevel';
import { calculateDetailCost } from './detailCalculateCost';

/**
 * Bu fonksiyon, master maliyet hesaplama butonunun davranışını yönetir.
 * Her buton tıklandığında, tüm hesaplamalar en güncel değerlere göre gerçekleştirilir.
 * 
 * - En yüksek seviyedeki tüm satırların güncel maliyetlerini hesaplar
 * - Bu maliyetleri toplayarak base cost'u (totalRowCost) bulur
 * - Master faktörlerle çarparak nihai maliyeti hesaplar
 * 
 * @param {Array} bomComponents - BOM bileşenlerinin bulunduğu dizi
 * @param {Object} dailyRatesMapping - Günlük kur değerlerini içeren obje
 * @param {Object} masterFactors - Master faktörleri içeren obje
 * @returns {Object} Hesaplama sonuçlarını içeren obje
 */
export function calculateMasterCostButton(bomComponents = [], dailyRatesMapping = {}, masterFactors = {}) {
  // Master faktörleri
  const {
    laborMultiplier = 1,
    overheadMultiplier = 1,
    licenseMultiplier = 1,
    commissionMultiplier = 1
  } = masterFactors;

  // En büyük seviyeyi bul
  const maxLevel = getMaxPositiveLevel(bomComponents);
  
  // Son seviyedeki tüm satırların güncel maliyetlerini hesapla
  const rowCosts = bomComponents.map(row => {
    // Eğer maksimum seviyedeyse güncel maliyeti hesapla
    if (Number(row.level) === maxLevel) {
      return calculateDetailCost(row, maxLevel, dailyRatesMapping);
    }
    return 0;
  });
  
  // Toplam satır maliyeti
  const totalRowCost = rowCosts.reduce((sum, cost) => sum + cost, 0);
  
  // Master faktörlerle çarpılmış nihai maliyet
  const finalCost = totalRowCost * 
    Number(laborMultiplier) * 
    Number(overheadMultiplier) * 
    Number(licenseMultiplier) * 
    Number(commissionMultiplier);
  
  // Hesaplama değişkenlerini logla
  console.log(`Master Maliyet Hesaplama:
    Toplam Satır Maliyeti: ${totalRowCost}
    İşçilik Çarpanı: ${laborMultiplier}
    Genel Üretim Çarpanı: ${overheadMultiplier}
    Lisans Çarpanı: ${licenseMultiplier}
    Komisyon Çarpanı: ${commissionMultiplier}
    Nihai Maliyet: ${finalCost}`
  );
  
  return {
    baseCost: totalRowCost,
    finalCost: finalCost,
    // Her bir faktörün uygulanmış değerini de döndür
    laborEffect: totalRowCost * laborMultiplier,
    overheadEffect: totalRowCost * laborMultiplier * overheadMultiplier,
    licenseEffect: totalRowCost * laborMultiplier * overheadMultiplier * licenseMultiplier,
    commissionEffect: finalCost
  };
}

/**
 * Tablo verilerini kullanarak maliyet hesaplama butonunu çalıştıran yardımcı fonksiyon.
 * Butona her basıldığında bu fonksiyon çağrılabilir.
 * 
 * @param {Array} tableData - Tablo verileri
 * @param {Object} dailyRates - Günlük kur değerleri
 * @param {Object} factorValues - Master faktör değerleri
 * @param {Function} setUpdatedCost - State güncellemek için kullanılacak setter fonksiyonu
 */
export function executeMasterCostCalculation(tableData, dailyRates, factorValues, setUpdatedCost) {
  // Yeni bir hesaplama yap
  const result = calculateMasterCostButton(tableData, dailyRates, factorValues);
  
  // Sonucu state'e kaydet
  setUpdatedCost(result.finalCost);
  
  // Butona basıldığını logla
  console.log("Maliyet Hesaplama Butonu: Hesaplama tamamlandı.");
  
  return result;
}