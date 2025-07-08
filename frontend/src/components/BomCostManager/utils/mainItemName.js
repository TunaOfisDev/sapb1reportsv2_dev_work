// frontend/src/components/BomCostManager/utils/mainItemName.js
/**
 * BOM verileri arasından (level = -1) ana ürüne ait ismi bulur.
 * 
 * @param {Array} bomComponents - BOM bileşenlerinin listesi
 * @returns {string} Ana ürünün component_item_name değeri
 */
export function getMainItemName(bomComponents) {
    if (!Array.isArray(bomComponents) || bomComponents.length === 0) {
      return '';
    }
  
    // level = -1 olan kaydı bul
    const mainItem = bomComponents.find(item => Number(item.level) === -1);
    if (!mainItem) {
      return '';
    }
  
    // Kayıttan component_item_name veya ComponentItemName alanını döndür
    // Projenizdeki JSON/Model'e göre "component_item_name" ya da "ComponentItemName" olabilir
    return mainItem.component_item_name || mainItem.ComponentItemName || '';
  }
  