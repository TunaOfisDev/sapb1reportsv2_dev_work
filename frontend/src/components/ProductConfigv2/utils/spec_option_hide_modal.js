/**
 * ETAJER görünürlük kontrolü: 
 * ETAJER VAR MI? cevabına göre ilgili özellikleri ve seçenekleri göster/gizle
 *
 * @param {Object} selections - { specTypeId: optionId }
 * @param {Array} features - Ürüne ait tüm özellikler (specificationTypes)
 * @returns {Object} - { [specTypeId]: true | false } şeklinde görünürlük haritası
 */
export function getEtajerVisibilityMap(features, selections) {
  const visibilityMap = {};

  // 1. "ETAJER VAR MI?" alanını bul
  const etajerVarMiFeature = features.find((f) => {
    const specType = f.spec_type || f;
    return specType.name === 'ETAJER VAR MI?';
  });

  if (!etajerVarMiFeature) return visibilityMap;

  const specType = etajerVarMiFeature.spec_type || etajerVarMiFeature;
  const featureId = specType.id;
  const options = etajerVarMiFeature.options || [];

  const selectedOptionId = selections[featureId];
  const selectedOption = options.find(opt => opt.id.toString() === selectedOptionId?.toString());

  const etajerVisible = selectedOption?.name === 'EVET ETAJERLİ';

  features.forEach((f) => {
    const type = f.spec_type || f;
    const name = type.name?.toUpperCase?.() || '';

    if (name.includes('ETAJER') && name !== 'ETAJER VAR MI?') {
      visibilityMap[type.id] = etajerVisible;
    }
  });

  return visibilityMap;
}

  