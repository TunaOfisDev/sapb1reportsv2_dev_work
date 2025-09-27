// frontend/src/components/ProductConfigv2/components/Configurator/ConfigSubmitter.js
import React, { useState } from 'react';
import configApi from '../../api/configApi';
import '../../styles/ConfigSubmitter.css';
import { validateRequiredSelections } from '../../utils/configHelpers';

// GÜNCELLEME: onVariantCreated prop'u eklendi, successMessage mantığı kaldırıldı
const ConfigSubmitter = ({ product, selectedFeatures, projectName, isValid, onVariantCreated }) => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  // KALDIRILDI: Bu bileşen artık kendi başarı mesajını yönetmiyor.
  // const [successMessage, setSuccessMessage] = useState(null);

  const handleCreateVariant = async () => {
    setLoading(true);
    setError(null);
    
    // 1. Proje Adı'nın zorunlu olduğunu kontrol et
    if (!projectName || projectName.trim() === '') {
      setLoading(false);
      setError({ message: 'Proje Adı Zorunlu', details: 'Lütfen bir proje adı girin.' });
      return;
    }

    // 2. Genel Kural Geçerliliği Kontrolü
    if (!isValid) {
      setLoading(false);
      setError({ message: 'Geçersiz Kombinasyon', details: 'Lütfen seçiminizi kontrol edin.' });
      return;
    }
    
    // 3. Zorunlu Alanların Seçilip Seçilmediği Kontrolü
    const { isValid: requiredValid, missingNames } = validateRequiredSelections(product, selectedFeatures);
    if (!requiredValid) {
      setLoading(false);
      setError({ message: 'Zorunlu Alanlar Eksik', details: `Lütfen şu özellikleri seçin: ${missingNames.join(', ')}` });
      return;
    }

    try {
      const data = {
        product_id: product.id,
        project_name: projectName,
        selections: selectedFeatures,
      };
      const response = await configApi.createVariant(data);
      if (response.status === 201) {
        // GÜNCELLEME: Başarı durumunda, gelen veriyi parent component'e bildiriyoruz.
        if (onVariantCreated) {
          onVariantCreated(response.data);
        }
      }
    } catch (err) {
      const errorDetails = err.response?.data;
      setError({ message: "Varyant oluşturulamadı", details: errorDetails?.detail || err.message });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="config-submitter">
      <button className="config-submitter__btn" onClick={handleCreateVariant} disabled={loading || !isValid}>
        {loading ? 'Oluşturuluyor...' : 'Varyant Oluştur'}
      </button>
      {error && (
        <div className="config-submitter__error">
          <strong>{error.message}</strong>
          {error.details && <div>Detay: {typeof error.details === 'object' ? JSON.stringify(error.details) : error.details}</div>}
        </div>
      )}
      {/* KALDIRILDI: Başarı mesajı JSX'i buradan kaldırıldı. Bu artık ConfiguratorMain'in sorumluluğunda. */}
    </div>
  );
};

export default ConfigSubmitter;