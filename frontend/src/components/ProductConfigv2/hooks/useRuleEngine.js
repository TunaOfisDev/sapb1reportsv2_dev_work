// frontend/src/components/ProductConfigv2/hooks/useRuleEngine.js
import { useState, useEffect } from 'react';
import configApi from '../api/configApi';

const useRuleEngine = () => {
  const [rules, setRules] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const fetchRules = async () => {
    setLoading(true);
    try {
      const response = await configApi.getRules();
      if (response.data && response.data.results) {
        setRules(response.data.results);
      }
    } catch (err) {
      setError(err);
    }
    setLoading(false);
  };

  useEffect(() => {
    fetchRules();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const evaluateRules = (selections, specificationTypes = []) => {
    let isValid = true;
    let feedback = '';
    const tooltipWarnings = {};
    

    
    // Özellik ID'leri ve isimleri arasında eşleştirme oluştur
    const featureNameToIdMap = {};
    const featureIdToNameMap = {};
    specificationTypes.forEach(spec => {
      const specType = spec.spec_type || spec;
      featureNameToIdMap[specType.name] = specType.id;
      featureIdToNameMap[specType.id] = specType.name;
    });
    
    // Seçimleri isim bazlı objeye dönüştür
    const selectionsByName = {};
    // selectionsByName objesi oluşturulurken:
  for (const featureId in selections) {
    if (featureIdToNameMap[featureId]) {
      const featureName = featureIdToNameMap[featureId];
      const selectedOptionId = selections[featureId];

      if (selectedOptionId == null) continue; // <-- NULL ya da undefined ise geç

      const feature = specificationTypes.find(spec => {
        const specType = spec.spec_type || spec;
        return specType.id.toString() === featureId.toString();
      });

      if (feature) {
        const specType = feature.spec_type || feature;
        const option = specType.options.find(opt =>
          opt.id != null && selectedOptionId != null &&
          opt.id.toString() === selectedOptionId.toString()
        );

        if (option) {
          selectionsByName[featureName] = option.name;
        }
      }
    }
  }

    
    rules.forEach(rule => {
      // --- DENY KURALLARI (kombinasyon geçersiz kılma)
      if (rule.rule_type === 'deny' && rule.conditions) {
        let ruleMatch = true;
        
        if (Object.keys(rule.conditions).some(key => !isNaN(parseInt(key)))) {
          for (const featureId in rule.conditions) {
            if (selections[featureId] !== rule.conditions[featureId]) {
              ruleMatch = false;
              break;
            }
          }
        } else {
          for (const featureName in rule.conditions) {
            const expectedOptionName = rule.conditions[featureName];
            const actualOptionName = selectionsByName[featureName];
            
            if (actualOptionName !== expectedOptionName) {
              ruleMatch = false;
              break;
            }
          }
        }
        
        if (ruleMatch) {
          isValid = false;
          feedback = rule.message || 'Seçtiğiniz kombinasyon geçersiz!';
        }
      }
      
      // --- ALLOW KURALLARI (seçime göre bazı speklerin zorunlu hale gelmesi)
      if (rule.rule_type === 'allow' && rule.conditions && rule.actions) {
        let match = true;
        
        if (Object.keys(rule.conditions).some(key => !isNaN(parseInt(key)))) {
          for (const featureId in rule.conditions) {
            if (selections[featureId] !== rule.conditions[featureId]) {
              match = false;
              break;
            }
          }
        } else {
          for (const featureName in rule.conditions) {
            const expectedOptionName = rule.conditions[featureName];
            const actualOptionName = selectionsByName[featureName];
            
            if (actualOptionName !== expectedOptionName) {
              match = false;
              break;
            }
          }
        }
        
        if (match && rule.actions.require) {
          rule.actions.require.forEach(req => {
            if (req.startsWith('__CONTAINS_SPEC__=')) {
              const keyword = req.split('=')[1];
              const matchedSpecs = specificationTypes.filter(spec => {
                const specType = spec.spec_type || spec;
                return specType.name.toLowerCase().includes(keyword.toLowerCase()) && 
                       specType.name !== "ETAJER VAR MI?";
              });

              // ETAJER VAR MI? kontrolü
              const triggerFeature = specificationTypes.find(spec => {
                const specType = spec.spec_type || spec;
                return specType.name === "ETAJER VAR MI?";
              });
              
              if (triggerFeature) {
                const triggerFeatureId = (triggerFeature.spec_type || triggerFeature).id;
                const selectedOption = selections[triggerFeatureId];
                const isTriggerActive = triggerFeature.options.some(
                  opt => opt.id === selectedOption && opt.name === "EVET ETAJERLİ"
                );

                if (isTriggerActive) {
                  // Tüm ETAJER özelliklerinin seçilme durumunu kontrol et
                  const missingSpecs = matchedSpecs.filter(spec => {
                    const specType = spec.spec_type || spec;
                    return !selections[specType.id];
                  });

                  if (missingSpecs.length > 0) {
                    isValid = false;
                    feedback = "TÜM ETAJER özellikleri zorunludur!";
                    missingSpecs.forEach(spec => {
                      const specType = spec.spec_type || spec;
                      tooltipWarnings[specType.id] = `"${specType.name}" zorunlu alan`;
                    });
                  }
                }
              }
            }
          });
        }
      }
    });
    
    
    return { isValid, feedback, tooltipWarnings };
  };

  const refreshRules = () => {
    fetchRules();
  };

  return { rules, loading, error, evaluateRules, refreshRules };
};

export default useRuleEngine;