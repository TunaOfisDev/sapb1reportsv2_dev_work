/**
 * Ürün konfigürasyonu için yardımcı fonksiyonlar.
 * Varsayılan seçimlerin belirlenmesi, fiyat hesaplaması, zorunlu özellik doğrulaması vb. işlemleri içerir.
 */

/**
 * Verilen fiyatı belirtilen para birimi formatında string'e çevirir.
 * Burada varsayılan olarak Almanya yerel ayarları ve EUR kullanılıyor.
 * @param {number|string} price - Fiyat değeri.
 * @param {string} currency - Para birimi (varsayılan: "EUR").
 * @returns {string} Formatlanmış fiyat (ör. "€300,00").
 */
export const formatPrice = (price, currency = "EUR") => {
  const priceNumber = typeof price === "number" ? price : parseFloat(price);
  return new Intl.NumberFormat("de-DE", {
    style: "currency",
    currency,
  }).format(priceNumber);
};

/**
 * Ürün özellik tipleri içerisindeki varsayılan seçenekleri seçer.
 * Eğer bir özellik tipinde default olarak işaretlenmiş bir seçenek yoksa, ilk seçeneği varsayılan kabul eder.
 * @param {Array} specificationTypes - Ürün özellik tipi dizisi.
 * @returns {Object} Varsayılan seçimler nesnesi (ör. { specTypeId: optionId, ... }).
 */
export const getDefaultSelections = (specificationTypes) => {
  const defaultSelections = {};
  if (Array.isArray(specificationTypes)) {
    specificationTypes.forEach((specType) => {
      if (specType.options && specType.options.length > 0) {
        const defaultOption =
          specType.options.find((option) => option.is_default) ||
          specType.options[0];
        defaultSelections[specType.id] = defaultOption.id;
      }
    });
  }
  return defaultSelections;
};

/**
 * Ürünün temel fiyatı ve seçili seçeneklerin fiyat farklarını toplayarak toplam fiyatı hesaplar.
 * Her seçenek nesnesi "price_delta" alanını içermelidir.
 * @param {number|string} basePrice - Ürünün temel fiyatı.
 * @param {Array} selectedOptions - Seçili seçenekler dizisi.
 * @returns {number} Toplam hesaplanan fiyat.
 */
export const calculateTotalPrice = (basePrice, selectedOptions) => {
  let total =
    typeof basePrice === "number" ? basePrice : parseFloat(basePrice);
  if (Array.isArray(selectedOptions)) {
    selectedOptions.forEach((option) => {
      const delta = parseFloat(option.price_delta) || 0;
      total += delta;
    });
  }
  return total;
};

/**
 * Temel fiyat ve seçili seçeneklerden hesaplanan toplam fiyatı formatlanmış şekilde döner.
 * @param {number|string} basePrice - Ürünün temel fiyatı.
 * @param {Array} selectedOptions - Seçili seçenekler dizisi.
 * @param {string} currency - Para birimi (varsayılan: "EUR").
 * @returns {string} Formatlanmış toplam fiyat.
 */
export const getFormattedTotalPrice = (
  basePrice,
  selectedOptions,
  currency = "EUR"
) => {
  const total = calculateTotalPrice(basePrice, selectedOptions);
  return formatPrice(total, currency);
};

/**
 * Bu fonksiyon, product.features dizisindeki her özellikte (is_required=true)
 * kullanıcının seçili bir seçenek olup olmadığını kontrol eder.
 *
 * @param {Object} product - API'den alınan ürün nesnesi (içinde features dizisi olmalı).
 * @param {Object} selectedFeatures - Özellik ID -> Seçenek ID şeklindeki seçimler.
 * @returns {{ isValid: boolean, missingNames: string[] }}
 *          isValid false ise, missingNames dizisi eksik özellik adlarını içerir.
 */
export const validateRequiredSelections = (product, selectedFeatures) => {
  if (!product || !Array.isArray(product.features)) {
    // Ürün özellikleri tanımlı değilse, geçerli sayalım.
    return { isValid: true, missingNames: [] };
  }

  const missingNames = [];

  product.features.forEach((featureObj) => {
    // Özellik bilgisi, bazı yapılarda featureObj.spec_type altında, bazı yapılarda doğrudan featureObj olabilir.
    const specData = featureObj.spec_type || featureObj;
    const specId = String(specData.id);
    const specName = specData.name;
    const isRequired = specData.is_required;

    // Eğer zorunlu özellik için, selectedFeatures içinde ilgili ID yoksa veya değeri falsy ise, eksik kabul et.
    if (isRequired && (!selectedFeatures.hasOwnProperty(specId) || !selectedFeatures[specId])) {
      missingNames.push(specName);
    }
  });

  return {
    isValid: missingNames.length === 0,
    missingNames,
  };
};


/**
 * Seçilen seçeneklerin gerçek nesnelerini ürünün options listesinden bulur.
 * Bu sayede price_delta gibi verilere erişim sağlanır.
 * @param {Object} product - Ürün nesnesi (features içinde spec_type ve options içerir).
 * @param {Object} selectedFeatures - {specTypeId: optionId} şeklinde kullanıcı seçimleri.
 * @returns {Array} Seçilen seçenek nesneleri.
 */
export const mapSelectedFeaturesToOptions = (product, selectedFeatures) => {
  const result = [];
  if (!product?.features) return result;

  product.features.forEach((featureObj) => {
    const specType = featureObj.spec_type || featureObj;
    const chosenOptionId = selectedFeatures[specType.id];
    if (!chosenOptionId || !Array.isArray(specType.options)) return;

    const selectedOption = specType.options.find(opt => opt.id === chosenOptionId);
    if (selectedOption) {
      result.push(selectedOption);
    }
  });

  return result;
};

// Varsayılan export
export default {
  formatPrice,
  getDefaultSelections,
  calculateTotalPrice,
  getFormattedTotalPrice,
  validateRequiredSelections,
  mapSelectedFeaturesToOptions,
};
