// frontend/src/components/ProductConfigv2/utils/priceCalculator.js

/**
 * Bu modül, ürünün toplam fiyatını hesaplamak için kullanılan fonksiyonları içerir.
 * Ürünün temel fiyatına, seçili seçeneklerin (price_delta) eklenmesiyle toplam fiyat hesaplanır.
 */

import { formatPrice } from './configHelpers';

/**
 * Seçili seçeneklerin fiyat delta'larının toplamını hesaplar.
 * Eğer bir seçeneğin price_delta değeri sayı değilse (NaN ise) sıfır kabul edilir.
 * @param {Array} selectedOptions - Seçili seçenekler dizisi.
 * @returns {number} Seçili seçeneklerden kaynaklanan ek fiyat.
 */
export const calculateOptionPrice = (selectedOptions) => {
  let additionalPrice = 0;
  if (Array.isArray(selectedOptions)) {
    selectedOptions.forEach((option) => {
      const delta = parseFloat(option.price_delta);
      additionalPrice += isNaN(delta) ? 0 : delta;
    });
  }
  return additionalPrice;
};

/**
 * Ürünün toplam fiyatını hesaplar.
 * Toplam fiyat = temel fiyat + seçili seçeneklerin ek fiyatı.
 * Eğer temel fiyat geçerli bir sayı değilse, sıfır kabul edilir.
 * @param {number|string} basePrice - Ürünün temel fiyatı.
 * @param {Array} selectedOptions - Seçili seçenekler dizisi.
 * @returns {number} Hesaplanan toplam fiyat.
 */
export const calculatePrice = (basePrice, selectedOptions) => {
  let base = parseFloat(basePrice);
  if (isNaN(base)) {
    base = 0;
  }
  const additional = calculateOptionPrice(selectedOptions);
  return base + additional;
};

/**
 * Hesaplanan toplam fiyatı, belirtilen para birimi formatında string olarak döner.
 * Ürün fiyat dövizi daima EUR olacak şekilde varsayılan ayar yapılmıştır.
 * @param {number|string} basePrice - Ürünün temel fiyatı.
 * @param {Array} selectedOptions - Seçili seçenekler dizisi.
 * @param {string} currency - Para birimi (varsayılan: "EUR").
 * @returns {string} Formatlanmış toplam fiyat (ör. "€300,00").
 */
export const getFormattedPrice = (basePrice, selectedOptions, currency = "EUR") => {
  const totalPrice = calculatePrice(basePrice, selectedOptions);
  return formatPrice(totalPrice, currency);
};

export default {
  calculateOptionPrice,
  calculatePrice,
  getFormattedPrice,
};
