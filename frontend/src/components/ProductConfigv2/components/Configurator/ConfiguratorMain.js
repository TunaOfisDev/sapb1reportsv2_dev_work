// frontend/src/components/ProductConfigv2/components/Configurator/ConfiguratorMain.js
import React, { useState, useEffect, useMemo } from 'react';
import { useParams, Link } from 'react-router-dom';
import FeatureSection from './FeatureSection';
import ProductVisualization from './ProductVisualization';
import PriceSummary from './PriceSummary';
import RuleFeedback from './RuleFeedback';
import useConfigurator from '../../hooks/useConfigurator';
import useRuleEngine from '../../hooks/useRuleEngine';
import ConfigSubmitter from './ConfigSubmitter';
import { Menu } from 'lucide-react';
import { getEtajerVisibilityMap }  from '../../utils/spec_option_hide_modal';
import '../../styles/configurator.css';

const ConfiguratorMain = () => {
  const { productId } = useParams();
  const {
    product,
    selectedFeatures,
    price,
    loading,
    error,
    handleFeatureSelect,
    resetConfiguration,
  } = useConfigurator(productId);

  const { evaluateRules } = useRuleEngine();
  const [ruleValidation, setRuleValidation] = useState({
    isValid: true,
    feedback: '',
    tooltipWarnings: {}
  });

  const visibleFeaturesMap = useMemo(() => {
    return getEtajerVisibilityMap(product?.features || [], selectedFeatures);
  }, [product, selectedFeatures]);

  useEffect(() => {
    if (product && product.features) {
      const result = evaluateRules(selectedFeatures, product.features || []);
      setRuleValidation(result);
    }
  }, [selectedFeatures, product, evaluateRules]);

  if (loading) return <div>Yükleniyor...</div>;
  if (error) return <div>Hata: {error.message}</div>;
  if (!product) return <div>Ürün bulunamadı.</div>;

  const mandatoryFeatures = (product.features || []).filter(f => f.is_required);
  const optionalFeatures = (product.features || []).filter(f => !f.is_required);

  const hasWarnings = Object.keys(ruleValidation.tooltipWarnings).length > 0;

  return (
    <div className="product-config">
      <header className="product-config__header">
        <h1>{product.name}</h1>
        <div className="product-config__header-actions">
          <Link to="/configurator-v2" className="product-config__back-link">
            <Menu size={18} />
            <span>Ürün Listesine Dön</span>
          </Link>
        </div>
      </header>

      {hasWarnings && (
        <div className="product-config__rule-warning">
          <i className="warning-icon">⚠️</i>
          <span>Bazı alanlar, yaptığınız seçimler dolayısıyla zorunlu hale gelmiştir.</span>
        </div>
      )}

      <div className="product-config__body">
        <div className="product-config__body-left">
          <div className="features-dual-container">
            <div className="features-dual-column">
              <h2>Zorunlu Alanlar</h2>
              <FeatureSection
                features={mandatoryFeatures}
                selectedFeatures={selectedFeatures}
                onFeatureSelect={handleFeatureSelect}
                tooltipWarnings={ruleValidation.tooltipWarnings}
                visibleFeaturesMap={visibleFeaturesMap}
              />

            </div>
            <div className="features-dual-column">
              <h2>Opsiyonel Alanlar</h2>
              <FeatureSection
                  features={optionalFeatures}
                  selectedFeatures={selectedFeatures}
                  onFeatureSelect={handleFeatureSelect}
                  tooltipWarnings={ruleValidation.tooltipWarnings}
                  visibleFeaturesMap={visibleFeaturesMap}
                />

            </div>
          </div>
        </div>

        <div className="product-config__body-right">
          {!ruleValidation.isValid && <RuleFeedback feedback={ruleValidation.feedback} />}
          <footer className="product-config__footer">
            <button
              className="product-config__reset-btn"
              onClick={resetConfiguration}
            >
              Konfigürasyonu Sıfırla
            </button>
            <ConfigSubmitter
              product={product}
              selectedFeatures={selectedFeatures}
              isValid={ruleValidation.isValid}
              tooltipWarnings={ruleValidation.tooltipWarnings}
              visibleFeaturesMap={visibleFeaturesMap}
            />
          </footer>

          <PriceSummary
            basePrice={product.base_price}
            specificationTypes={product.features}
            selections={selectedFeatures}
            currency={product.currency}
          />

          <ProductVisualization
            product={product}
            selectedFeatures={selectedFeatures}
          />
        </div>
      </div>
    </div>
  );
};

export default ConfiguratorMain;