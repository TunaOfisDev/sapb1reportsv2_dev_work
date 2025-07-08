// frontend/src/components/BomCostManager/utils/masterCalculateCost.js
import { getMaxPositiveLevel } from './getMaxPositiveLevel';

/**
 * Bu fonksiyon, verilen BOM bileşenleri arasında "en büyük BOM seviyesi"ndeki kalemleri bulur,
 * bu kalemlerin "Bileşen Maliyeti" (component_cost_upb) ve "Güncel Maliyet" (updated_cost)
 * toplamlarını hesaplar. Ek olarak, verilen master faktörler (işçilik, overhead, lisans, komisyon)
 * ile manipüle edilmiş güncel maliyeti hesaplar.
 *
 * @param {Array} bomComponents - BOM bileşenlerinin bulunduğu dizi.
 * @param {Object} masterFactors - Master faktörleri içeren obje:
 *    { laborMultiplier, overheadMultiplier, licenseMultiplier, commissionMultiplier }
 * @returns {Object} { totalComponentCost, totalUpdatedCost, manipulatedUpdatedCost }
 */
export function calculateMasterCost(bomComponents = [], masterFactors = {}) {
  // En büyük pozitif level'ı bulalım
  const maxLevel = getMaxPositiveLevel(bomComponents);

  // Sadece maxLevel'e sahip kalemleri filtrele
  const lastLevelComponents = bomComponents.filter(item => Number(item.level) === maxLevel);

  // Toplam Bileşen Maliyeti (component_cost_upb) hesaplama
  const totalComponentCost = lastLevelComponents.reduce((sum, item) => {
    return sum + Number(item.component_cost_upb || 0);
  }, 0);

  // Detay Güncel Maliyet (updated_cost) hesaplama
  const totalUpdatedCost = lastLevelComponents.reduce((sum, item) => {
    return sum + Number(item.updated_cost || 0);
  }, 0);

  // Master faktörler; varsayılan değer 1
  const {
    laborMultiplier = 1,
    overheadMultiplier = 1,
    licenseMultiplier = 1,
    commissionMultiplier = 1
  } = masterFactors;

  // Manipüle edilmiş güncel maliyet:
  // Temel bileşen maliyetini (totalComponentCost) master faktörlerle çarpıyoruz
  const manipulatedUpdatedCost =
    totalComponentCost *
    Number(laborMultiplier) *
    Number(overheadMultiplier) *
    Number(licenseMultiplier) *
    Number(commissionMultiplier);

  return {
    totalComponentCost,
    totalUpdatedCost,
    manipulatedUpdatedCost
  };
}
