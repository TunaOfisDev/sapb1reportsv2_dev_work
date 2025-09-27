/**
 * BOM bileşenlerinin nihai maliyetini hesaplamak için yardımcı fonksiyonlar.
 * 
 * Master ve detay seviyeleri ayrıştırılmıştır:
 *  - Satır bazında maliyet hesaplamak için `calculateComponentCost`
 *  - Satır maliyetlerinin toplamını almak için `calculateTotalCost`
 *  - Master çarpanlarla nihai BOM maliyetini hesaplamak için `calculateMasterCost`
 */

/**
 * Tek bir bileşenin satır bazında maliyetini hesaplar.
 * Master çarpanlar hariç tutulur.
 * 
 * @param {Object} component - BOM bileşeni (new_last_purchase_price, last_purchase_price_upb, quantity)
 * @returns {number} rowCost - Tek satırın maliyeti
 */
export function calculateComponentCost(component) {
  if (!component) return 0;

  const {
      new_last_purchase_price = 0,
      last_purchase_price_upb = 0,
      quantity = 1
  } = component;

  // Override edilen fiyat varsa onu kullan, yoksa last_purchase_price_upb kullan
  const effectivePrice = new_last_purchase_price > 0 ? new_last_purchase_price : last_purchase_price_upb;

  // Satır maliyeti = (etkin fiyat) * (miktar)
  const rowCost = effectivePrice * Number(quantity);
  return Number(rowCost.toFixed(2));
}

/**
* Bir BOM içerisindeki tüm bileşenlerin satır maliyetini toplayarak toplam maliyet hesaplar.
* (Master çarpanlar HARİÇ!)
* 
* @param {Array} components - Bileşenler listesi
* @returns {number} totalRowCost - Master çarpanlar uygulanmadan önceki toplam maliyet
*/
export function calculateTotalCost(components = []) {
  if (!Array.isArray(components)) return 0;

  return components.reduce((acc, comp) => {
      const cost = calculateComponentCost(comp);
      return acc + cost;
  }, 0);
}

/**
* Master çarpanlar (İşçilik, Genel Üretim, Lisans, Komisyon) uygulanarak nihai maliyeti hesaplar.
* 
* @param {number} baseCost - Tüm satırların toplam maliyeti (totalRowCost)
* @param {Object} multipliers - Master çarpanlar { labor, overhead, license, commission }
* @returns {number} finalCost - Nihai BOM maliyeti
*/
export function calculateMasterCost(baseCost, multipliers = {}) {
  const {
      labor = 1,
      overhead = 1,
      license = 1,
      commission = 1
  } = multipliers;

  // Nihai maliyet hesaplama
  const finalCost = baseCost * labor * overhead * license * commission;
  return Number(finalCost.toFixed(2));
}
