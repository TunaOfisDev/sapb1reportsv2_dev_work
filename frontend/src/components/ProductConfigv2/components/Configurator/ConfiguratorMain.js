// frontend/src/components/ProductConfigv2/components/Configurator/ConfiguratorMain.js
import React, { useState, useEffect, useMemo } from 'react';
import { useParams, Link } from 'react-router-dom';
import FeatureSection from './FeatureSection';
import ProductVisualization from './ProductVisualization';
import RuleFeedback from './RuleFeedback';
import useConfigurator from '../../hooks/useConfigurator';
import useRuleEngine from '../../hooks/useRuleEngine';
import ConfigSubmitter from './ConfigSubmitter';
import { Menu, List } from 'lucide-react';
import toUpperCaseTurkish from '../../utils/toUpperCaseTurkish';
import configApi from '../../api/configApi';
import { getEtajerVisibilityMap } from '../../utils/spec_option_hide_modal';
import '../../styles/configurator.css';

const ConfiguratorMain = () => {
  const { productId } = useParams();
  const {
    product,
    selectedFeatures,
    loading,
    error,
    handleFeatureSelect,
    resetConfiguration,
    projectName,
    setProjectName,
  } = useConfigurator(productId);

  const { evaluateRules } = useRuleEngine();
  const [ruleValidation, setRuleValidation] = useState({ isValid: true, feedback: '', tooltipWarnings: {} });
  
  const [createdVariant, setCreatedVariant] = useState(null);
  const handleResetClick = () => {
    resetConfiguration(); // Hook içindeki seçimleri, proje adını vb. sıfırlar
    setCreatedVariant(null); // Başarı mesajını ve "Fiyatı Güncelle" butonunu kaldırır
  };
  const [priceLoading, setPriceLoading] = useState(false);
  const [priceError, setPriceError] = useState(null);

  const visibleFeaturesMap = useMemo(() => {
    return getEtajerVisibilityMap(product?.features || [], selectedFeatures);
  }, [product, selectedFeatures]);

  useEffect(() => {
    if (product && product.features) {
      const result = evaluateRules(selectedFeatures, product.features || []);
      setRuleValidation(result);
    }
  }, [selectedFeatures, product, evaluateRules]);

  const handleVariantCreated = (variantData) => {
    setCreatedVariant(variantData);
  };
  
  const handlePriceUpdate = async (variantId) => {
    setPriceLoading(true);
    setPriceError(null);
    try {
      const response = await configApi.updateVariantPriceFromSap(variantId);
      setCreatedVariant(response.data);
    } catch (err) {
      setPriceError("SAP'den fiyat güncellenemedi.");
    } finally {
      setPriceLoading(false);
    }
  };

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
          {/* YENİ EKLENEN BUTON */}
          <Link to="/variants" className="product-config__back-link">
            <List size={18} />
            <span>Varyant Listesi</span>
          </Link>
          
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
        {/* EKSİK OLAN SOL TARAF KODU EKLENDİ */}
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
            {optionalFeatures.length > 0 && (
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
            )}
          </div>
        </div>

        <div className="product-config__body-right">
          <div className="summary-wrapper">
            {!ruleValidation.isValid && <RuleFeedback feedback={ruleValidation.feedback} />}
            <div className="form-group project-name-group">
              <label htmlFor="projectName">Proje Adı (max karakter sayısı 200) </label>
              <input type="text" id="projectName" className="project-name-input"
                placeholder="PROJE - MÜŞTERİ ADI GİRİNİZ!" value={projectName}
                onChange={(e) => setProjectName(toUpperCaseTurkish(e.target.value))}
                maxLength={200}
                disabled={!!createdVariant}
              />
            </div>
            
            <footer className="product-config__footer">
              <button className="product-config__reset-btn" onClick={handleResetClick}>
              Konfigürasyonu Sıfırla
            </button>
              <ConfigSubmitter
                product={product}
                selectedFeatures={selectedFeatures}
                projectName={projectName}
                isValid={ruleValidation.isValid}
                onVariantCreated={handleVariantCreated}
              />
            </footer>
            
            {createdVariant && (
              <div className="config-submitter__success">
                <h4>Varyant Başarıyla Oluşturuldu</h4>
                <p><strong>Proje Adı:</strong> {createdVariant.project_name || 'Belirtilmedi'}</p>
                <p><strong>Referans Kod (55'li):</strong> {createdVariant.reference_code}</p>
                <p><strong>Üretim Kodu (30'lu):</strong> {createdVariant.new_variant_code}</p>
                <p><strong>Açıklama:</strong> {createdVariant.new_variant_description}</p>
                <p><strong>Fiyat:</strong> {new Intl.NumberFormat("de-DE", { style: "currency", currency: "EUR" }).format(createdVariant.total_price)}</p>
                
                <div className="price-query-section" style={{marginTop: '1rem'}}>
                   <button onClick={() => handlePriceUpdate(createdVariant.id)}
                           className="price-query-button" disabled={priceLoading}>
                     {priceLoading ? 'Güncelleniyor...' : "Fiyatı SAP'den Güncelle"}
                   </button>
                   {priceError && <div className="price-error" style={{marginTop: '0.5rem'}}>{priceError}</div>}
                </div>
              </div>
            )}
            
            <ProductVisualization product={product} selectedFeatures={selectedFeatures} />
          </div>
        </div>
      </div>
    </div>
  );
};

export default ConfiguratorMain;