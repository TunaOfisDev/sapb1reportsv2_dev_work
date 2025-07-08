// frontend/src/components/ProductConfigv2/components/Configurator/ConfigSubmitter.js
import React, { useState } from 'react';
import configApi from '../../api/configApi';
import '../../styles/ConfigSubmitter.css';
import { validateRequiredSelections } from '../../utils/configHelpers';
import useRuleEngine from '../../hooks/useRuleEngine';

const ConfigSubmitter = ({ product, selectedFeatures, onVariantCreated, isValid, tooltipWarnings = {}, visibleFeaturesMap = {} }) => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [successMessage, setSuccessMessage] = useState(null);

  const { evaluateRules } = useRuleEngine();

  const handleCreateVariant = async () => {
    setLoading(true);
    setError(null);
    setSuccessMessage(null);

    if (isValid === false) {
      setLoading(false);
      setError({
        message: 'Kurallar gereği bu kombinasyon geçersiz',
        details: 'Lütfen geçerli bir kombinasyon seçin. Aksiyon veya zorunlu seçim kuralına takılıyor olabilir.'
      });
      return;
    }

    const { isValid: rulesValid, feedback, tooltipWarnings: warnings } = evaluateRules(selectedFeatures, product.features || []);

    if (!rulesValid) {
      setLoading(false);
      setError({
        message: "Varyant oluşturulamadı",
        details: feedback || "Geçersiz kombinasyon"
      });
      return;
    }

    if (Object.keys(warnings || {}).length > 0) {
      setLoading(false);
      setError({
        message: `Zorunlu alanlar eksik`,
        details: feedback || "Lütfen tüm zorunlu alanları doldurun"
      });
      return;
    }

    const { isValid: requiredValid, missingNames } = validateRequiredSelections(product, selectedFeatures);
    if (!requiredValid) {
      setLoading(false);
      setError({
        message: 'Zorunlu seçim eksik',
        details: `Aşağıdaki özelliklerden en az bir seçenek seçmelisiniz: ${missingNames.join(', ')}`
      });
      return;
    }

    // ETAJER özel kontrolü yine kalsın
    const etajerVarMi = product.features.find(f => {
      const specType = f.spec_type || f;
      return specType.name === "ETAJER VAR MI?";
    });

    if (etajerVarMi) {
      const etajerVarMiId = (etajerVarMi.spec_type || etajerVarMi).id;
      const etajerVarMiOptionId = selectedFeatures[etajerVarMiId];

      if (etajerVarMiOptionId) {
        const option = (etajerVarMi.spec_type || etajerVarMi).options.find(
          o => o.id.toString() === etajerVarMiOptionId.toString()
        );

        if (option && option.name === "EVET ETAJERLİ") {
          const etajerOzellikleri = product.features.filter(f => {
            const specType = f.spec_type || f;
            return specType.name.includes("ETAJER") && specType.name !== "ETAJER VAR MI?";
          });

          const herhangiEtajerDolu = etajerOzellikleri.some(f => {
            const specType = f.spec_type || f;
            return selectedFeatures[specType.id];
          });

          if (!herhangiEtajerDolu && etajerOzellikleri.length > 0) {
            setLoading(false);
            setError({
              message: "ETAJER ile ilgili seçim eksik",
              details: "ETAJER VAR MI? sorusuna EVET ETAJERLİ cevabı verildiğinde, en az bir ETAJER özelliği seçilmelidir."
            });
            return;
          }
        }
      }
    }

    try {
      // 🔍 Sadece görünür ve seçili olanlar gönderilecek
      const filteredSelections = Object.fromEntries(
        Object.entries(selectedFeatures).filter(([specId, val]) =>
          val != null && visibleFeaturesMap?.[specId] !== false
        )
      );

      const data = {
        product_id: product.id,
        selections: filteredSelections,
      };

      const response = await configApi.createVariant(data);

      if (response.status === 201) {
        const variantData = response.data;

        const codeLength = variantData.new_variant_code?.length || 0;
        const descriptionLength = variantData.new_variant_description?.length || 0;

        if (codeLength > 50) {
          setError({
            message: "Varyant kodu 50 karakteri aşıyor",
            details: "Varyant kodu en fazla 50 karakter olabilir. Lütfen sistem yöneticisine başvurun."
          });
          return;
        }

        if (descriptionLength > 200) {
          setError({
            message: "Varyant açıklaması 200 karakteri aşıyor",
            details: "Lütfen sistem yöneticisine başvurun."
          });
          return;
        }

        setSuccessMessage({
          title: "Varyant Başarıyla Oluşturuldu",
          details: {
            code: variantData.new_variant_code,
            description: variantData.new_variant_description,
            price: `${variantData.total_price} ${variantData.currency}`,
            codeLength,
            descriptionLength,
            selections: variantData.selections.map(sel => ({
              spec: sel.spec_type,
              option: sel.option,
            })),
          },
        });

        if (onVariantCreated) onVariantCreated(variantData);
      } else {
        setError({ message: `Beklenmedik durum: ${response.status}` });
      }
    } catch (err) {
      console.error("Varyant oluşturma hatası:", err);
      const errorDetails = err.response?.data;
      setError({
        message: "Varyant oluşturulamadı",
        details: errorDetails?.detail || errorDetails || err.message,
      });
    } finally {
      setLoading(false);
    }
  };

  const hasWarnings = Object.keys(tooltipWarnings).length > 0;

  return (
    <div className="config-submitter">
      {hasWarnings && (
        <div className="config-submitter__warnings">
          <p>⚠️ Bazı opsiyonel alanlar seçimleriniz nedeniyle zorunlu hale gelmiştir.</p>
        </div>
      )}

      <button 
        className="config-submitter__btn"
        onClick={handleCreateVariant} 
        disabled={loading || isValid === false || hasWarnings}
      >
        {loading ? 'Oluşturuluyor...' : 'Varyant Oluştur'}
      </button>

      {error && (
        <div className="config-submitter__error">
          <strong>{error.message}</strong>
          {error.details && <div>Detay: {error.details}</div>}
        </div>
      )}

      {successMessage && (
        <div className="config-submitter__success">
          <h4>{successMessage.title}</h4>
          <p><strong>Kod:</strong> {successMessage.details.code}</p>
          <p><strong>Açıklama:</strong> {successMessage.details.description}</p>
          <p><strong>Fiyat:</strong> {successMessage.details.price}</p>
          <p><strong>Kod uzunluk:</strong> {successMessage.details.codeLength}/50</p>
          <p><strong>Açıklama uzunluk:</strong> {successMessage.details.descriptionLength}/200</p>

          <div className="mt-3">
            <h5>Seçimler:</h5>
            <ul>
              {successMessage.details.selections.map((sel, index) => (
                <li key={index}>
                  <strong>{sel.spec}:</strong> {sel.option}
                </li>
              ))}
            </ul>
          </div>
        </div>
      )}
    </div>
  );
};

export default ConfigSubmitter;