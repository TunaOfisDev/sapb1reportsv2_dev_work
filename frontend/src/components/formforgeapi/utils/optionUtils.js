// path: frontend/src/components/formforgeapi/utils/optionUtils.js

/**
 * FormField Seçenekleri için Yardımcı Fonksiyonlar
 * --------------------------------------------------------------------
 * Bu dosya, bir form alanının (FormField) seçeneklerini ('select', 'radio' vb.)
 * yönetmek için kullanılan saf (pure) ve değişmez (immutable) yardımcı
 * fonksiyonları içerir.
 *
 * Her fonksiyon, mevcut bir `field` nesnesi alır ve state'i doğrudan
 * değiştirmek yerine, güncellenmiş bir `field` nesnesinin YENİ bir kopyasını döndürür.
 * Bu, React'in state yönetimi prensipleriyle uyumludur.
 */

/**
 * Bir alana yeni, boş bir seçenek ekler.
 * @param {Object} field - Güncellenecek form alanı nesnesi.
 * @returns {Object} - Yeni seçeneğin eklendiği, güncellenmiş alan nesnesinin bir kopyası.
 */
export const addOption = (field) => {
  if (!field || !Array.isArray(field.options)) {
    console.error("addOption: Geçersiz alan veya seçenekler dizisi yok.", field);
    return field;
  }

  const newOption = {
    // Backend'e kaydedilmeden önce geçici, benzersiz bir ID.
    // 'temp-' öneki, bunun henüz kaydedilmemiş bir öğe olduğunu belirtir.
    id: `temp-${Date.now()}`,
    label: "", // Başlangıçta boş bir etiket
    order: field.options.length, // Yeni seçeneği sona ekle
  };

  return {
    ...field, // Alanın geri kalanını kopyala
    options: [...field.options, newOption], // Mevcut seçenekleri kopyala ve yenisini ekle
  };
};

/**
 * Belirli bir seçeneğin etiketini günceller.
 * @param {Object} field - Güncellenecek form alanı nesnesi.
 * @param {string|number} optionId - Etiketi güncellenecek seçeneğin ID'si.
 * @param {string} newLabel - Seçenek için yeni etiket değeri.
 * @returns {Object} - İlgili seçeneğin güncellendiği, alan nesnesinin bir kopyası.
 */
export const updateOption = (field, optionId, newLabel) => {
  if (!field || !Array.isArray(field.options)) {
    console.error("updateOption: Geçersiz alan veya seçenekler dizisi yok.", field);
    return field;
  }

  const updatedOptions = field.options.map((option) => {
    if (option.id === optionId) {
      return { ...option, label: newLabel }; // Eşleşen seçeneğin etiketini güncelle
    }
    return option; // Diğerlerini olduğu gibi bırak
  });

  return {
    ...field,
    options: updatedOptions,
  };
};

/**
 * Bir alanı seçenek listesinden kaldırır ve kalanların sırasını yeniden düzenler.
 * @param {Object} field - Güncellenecek form alanı nesnesi.
 * @param {string|number} optionId - Kaldırılacak seçeneğin ID'si.
 * @returns {Object} - İlgili seçeneğin kaldırıldığı ve sıralamanın güncellendiği alan nesnesinin bir kopyası.
 */
export const removeOption = (field, optionId) => {
  if (!field || !Array.isArray(field.options)) {
    console.error("removeOption: Geçersiz alan veya seçenekler dizisi yok.", field);
    return field;
  }

  const filteredOptions = field.options.filter(
    (option) => option.id !== optionId
  );

  // Kalan seçeneklerin 'order' değerlerini yeniden düzenle (0, 1, 2, ...)
  const reorderedOptions = filteredOptions.map((option, index) => ({
    ...option,
    order: index,
  }));

  return {
    ...field,
    options: reorderedOptions,
  };
};