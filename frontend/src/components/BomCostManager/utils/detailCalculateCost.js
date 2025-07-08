// frontend/src/components/BomCostManager/utils/detailCalculateCost.js

/**
 * BOM bileşen satır verisine göre detay güncel satır toplam maliyeti hesaplar.
 *
 * Hesaplama mantığı:
 * - Sadece "targetLevel" eşit olan kalemler için geçerlidir (örn. en büyük level).
 * - Eğer kullanıcı tarafından yeni girilen güncel birim fiyat varsa (new_last_purchase_price),
 *   o değer kullanılır; yoksa orijinal "last_purchase_price_upb" değeri kullanılır.
 * - İlgili döviz cinsi için, dailyRatesMapping nesnesinden günlük kur değeri alınır.
 * - Sonuç: (Birim Fiyat) * (Günlük Döviz Kuru) * (Miktar) = Detay Güncel Satır Toplam Maliyet (TRY)
 *
 * @param {Object} row - BOM bileşen satır verisi.
 * @param {number} targetLevel - Hesaplama yapılacak BOM seviyesi (örn. en büyük level).
 * @param {Object} dailyRatesMapping - Döviz kodlarını ve karşılık gelen günlük kur değerlerini içeren obje.
 *                                     Örnek: { USD: 18.90, EUR: 20.05, TRY: 1 }
 * @returns {number} - Hesaplanan detay güncel satır toplam maliyeti (TRY cinsinden)
 */
export function calculateDetailCost(row, targetLevel, dailyRatesMapping = {}) {
  // Sadece targetLevel'e eşit olan kalemlerde hesaplama yap
  if (Number(row.level) !== targetLevel) {
    return 0;
  }

  // Yeni girilen güncel birim fiyatı kullan, yoksa orijinal birim fiyat
  // Türkçe formatını işlemek için virgülleri noktalara çevir
  let unitPriceStr = String(row.new_last_purchase_price || row.last_purchase_price_upb || 0);
  unitPriceStr = unitPriceStr.replace(',', '.');
  const unitPrice = parseFloat(unitPriceStr);

  // Kullanıcı yeni döviz seçtiyse onu, yoksa orijinal döviz değerini kullanıyoruz
  const currency = row.new_currency || row.currency || 'TRY';

  // İlgili döviz için günlük kuru alıyoruz; bulunamazsa varsayılan 1 (TRY)
  const dailyRate = Number(dailyRatesMapping[currency] || 1);
  
  // Miktarı da Türkçe formatını işleyerek dönüştür
  let quantityStr = String(row.quantity || 0);
  quantityStr = quantityStr.replace(',', '.');
  const quantity = parseFloat(quantityStr);

  // Tüm değerleri kontrol et ve logla
  console.log(`Hesaplama için değerler:
    Birim Fiyat: ${unitPrice} ${currency}
    Döviz Kuru: ${dailyRate} TRY/${currency}
    Miktar: ${quantity}
    Hesaplanan Tutar: ${unitPrice * dailyRate * quantity} TRY`
  );

  // Toplam maliyet = birim fiyat * günlük kur * miktar
  return unitPrice * dailyRate * quantity;
}
