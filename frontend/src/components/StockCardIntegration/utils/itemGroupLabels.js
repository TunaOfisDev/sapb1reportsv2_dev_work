// path: frontend/src/components/StockCardIntegration/utils/itemGroupLabels.js

/**
 * SAP ItemsGroupCode değerlerini anlamlı etiketlere dönüştürür
 * 
 * Örn: 105 → "Mamul", 103 → "Ticari Mal", 112 → "Girsberger"
 */
const itemGroupLabels = {
  105: 'Mamul',
  112: 'Girsberger',
  103: 'Ticari Mal',
};

export const getItemGroupLabel = (code) => {
  return itemGroupLabels[code] || `Bilinmeyen Grup (${code})`;
};

export const getItemGroupOptions = () => {
  // Seçenekleri istenen sırayla (Mamul, Girsberger, Ticari Mal) döndür
  const orderedCodes = [105, 112, 103]; // Sıralama: Mamul (105), Girsberger (112), Ticari Mal (103)
  return orderedCodes.map((value) => ({
    value: parseInt(value, 10),
    label: itemGroupLabels[value],
  }));
};