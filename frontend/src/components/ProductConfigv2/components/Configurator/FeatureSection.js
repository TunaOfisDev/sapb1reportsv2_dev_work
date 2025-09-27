// frontend/src/components/ProductConfigv2/components/Configurator/FeatureSection.js
import React from 'react';
import PropTypes from 'prop-types';
import FeatureDropdown from './FeatureDropdown';

const FeatureSection = ({ features, selectedFeatures, onFeatureSelect, tooltipWarnings = {}, visibleFeaturesMap = {} }) => {
  return (
    <div className="feature-section-erp">
      {features.map((featureSpec) => {
        const specType = featureSpec.spec_type || featureSpec;

        // Eğer bu özellik gizlenmişse, atla (ETAJER kontrolü gibi)
        if (visibleFeaturesMap.hasOwnProperty(specType.id) && !visibleFeaturesMap[specType.id]) {
          return null;
        }

        return (
          <FeatureDropdown
            key={specType.id}
            feature={specType}
            selectedOptionId={selectedFeatures[specType.id]}
            onOptionSelect={(optionId) => onFeatureSelect(specType.id, optionId)}
            tooltipWarning={tooltipWarnings[specType.id]}
          />
        );
      })}
    </div>
  );
};


FeatureSection.propTypes = {
 features: PropTypes.array.isRequired,
 selectedFeatures: PropTypes.object.isRequired,
 onFeatureSelect: PropTypes.func.isRequired,
 tooltipWarnings: PropTypes.object
};

FeatureSection.defaultProps = {
 tooltipWarnings: {}
};

export default FeatureSection;