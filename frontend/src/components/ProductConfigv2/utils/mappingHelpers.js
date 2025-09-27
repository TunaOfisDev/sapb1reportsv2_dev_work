// frontend/src/components/ProductConfigv2/utils/mappingHelpers.js

export const mapSelectedFeaturesToOptions = (specificationTypes, selectedSelections) => {
    const selectedOptions = [];
  
    if (!Array.isArray(specificationTypes)) return selectedOptions;
  
    specificationTypes.forEach((specType) => {
      const chosenOptionId = selectedSelections[specType.id];
      if (!chosenOptionId || !specType.options) return;
  
      const foundOption = specType.options.find(opt => opt.id === chosenOptionId);
      if (foundOption) {
        selectedOptions.push(foundOption);
      }
    });
  
    return selectedOptions;
  };
  