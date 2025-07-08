// frontend/src/components/BomCostManager/utils/factorValuePlus.js

/**
 * Bu modül master faktör değerlerini artırmak ve azaltmak için dinamik fonksiyonlar içerir.
 * Faktör değerleri belirli adımlarla artırılabilir veya azaltılabilir.
 */

/**
 * Varsayılan artış/azalış değeri
 * Örneğin: 1 -> 1.05 -> 1.10 -> 1.15 şeklinde artış
 */
const DEFAULT_STEP = 0.05;

/**
 * Faktör değerinin alt limiti (bu değerin altına düşemez)
 */
const MIN_FACTOR = 0.01;

/**
 * Faktör değerini dinamik olarak artırır
 * 
 * @param {number} currentValue - Mevcut faktör değeri
 * @param {number} step - İsteğe bağlı artış adımı (varsayılan 0.05)
 * @returns {number} - Artırılmış faktör değeri
 */
export function increaseFactorValue(currentValue, step = DEFAULT_STEP) {
  // Değer sayı değilse veya geçersizse, 1 döndür
  if (isNaN(currentValue) || currentValue === null || currentValue === undefined) {
    console.warn('Geçersiz faktör değeri, 1 kullanılıyor');
    return 1;
  }
  
  // Değer hassasiyeti için yuvarlama yapılır (5 ondalık basamak)
  const newValue = Math.round((Number(currentValue) + step) * 100000) / 100000;
  
  console.log(`Faktör ${currentValue} -> ${newValue} olarak artırıldı`);
  return newValue;
}

/**
 * Faktör değerini dinamik olarak azaltır
 * Değer MIN_FACTOR (0.01) değerinin altına inemez
 * 
 * @param {number} currentValue - Mevcut faktör değeri
 * @param {number} step - İsteğe bağlı azalış adımı (varsayılan 0.05)
 * @returns {number} - Azaltılmış faktör değeri
 */
export function decreaseFactorValue(currentValue, step = DEFAULT_STEP) {
  // Değer sayı değilse veya geçersizse, 1 döndür
  if (isNaN(currentValue) || currentValue === null || currentValue === undefined) {
    console.warn('Geçersiz faktör değeri, 1 kullanılıyor');
    return 1;
  }
  
  // Değer, minimum değerin altına düşmemeli
  const newValue = Math.max(
    MIN_FACTOR,
    Math.round((Number(currentValue) - step) * 100000) / 100000
  );
  
  console.log(`Faktör ${currentValue} -> ${newValue} olarak azaltıldı`);
  return newValue;
}

/**
 * Faktör değerini belirli bir değere ayarlar
 * Değer MIN_FACTOR (0.01) değerinin altına inemez
 * 
 * @param {number} newValue - Ayarlanacak yeni değer
 * @returns {number} - Ayarlanmış faktör değeri
 */
export function setFactorValue(newValue) {
  // Değer sayı değilse veya geçersizse, 1 döndür
  if (isNaN(newValue) || newValue === null || newValue === undefined) {
    console.warn('Geçersiz faktör değeri, 1 kullanılıyor');
    return 1;
  }
  
  // Değer, minimum değerin altına düşmemeli
  const validValue = Math.max(MIN_FACTOR, Number(newValue));
  
  // Değer hassasiyeti için yuvarlama yapılır (5 ondalık basamak)
  const roundedValue = Math.round(validValue * 100000) / 100000;
  
  return roundedValue;
}

/**
 * Faktör artırma/azaltma butonları için özel bir kontrol bileşeni oluşturmak için
 * gerekli fonksiyonları bir araya getirir
 * 
 * @param {number} initialValue - Başlangıç değeri
 * @param {number} customStep - Özel artış/azalış adımı
 * @returns {Object} - Faktör kontrolü için gerekli fonksiyonlar
 */
export function createFactorControl(initialValue = 1, customStep = DEFAULT_STEP) {
  return {
    increase: () => increaseFactorValue(initialValue, customStep),
    decrease: () => decreaseFactorValue(initialValue, customStep),
    set: (value) => setFactorValue(value),
    step: customStep,
    minValue: MIN_FACTOR
  };
}