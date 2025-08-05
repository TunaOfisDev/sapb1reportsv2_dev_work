
// path: frontend/src/components/formforgeapi/containers/FormForgeApiContainer.jsx
import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';

// Sayfa Seviyesi Bileşenleri
import FormSchemaListScreen from '../components/page-level/FormSchemaListScreen';
import FormBuilderScreen from '../components/page-level/FormBuilderScreen';
import FormDataListScreen from '../components/page-level/FormDataListScreen';
import FormFillScreen from '../components/page-level/FormFillScreen';

/**
 * FormForgeApiContainer Bileşeni
 * --------------------------------------------------------------------
 * FormForgeAPI modülünün tamamı için bir "root" bileşeni ve yönlendirici (router)
 * görevi görür.
 *
 * Sorumlulukları:
 * - Modül içindeki tüm sayfa seviyesi bileşenler için URL yollarını tanımlar.
 * - Ana uygulama yönlendiricisinden (`App.js`) devraldığı `/formforge/*`
 * gibi yolları yönetir.
 * - Modül için genel bir layout veya context provider'ları (eğer gerekirse)
 * sarmalayabilir.
 */
const FormForgeApiContainer = () => {
  return (
    // İleride buraya modül geneli bir başlık, kenar çubuğu veya
    // bir context provider eklenebilir.
    <div className="formforgeapi-container">
      <Routes>
        {/* Ana yol, form şemalarının listelendiği ekrana yönlendirir */}
        <Route index element={<FormSchemaListScreen />} />

        {/* Form oluşturucu ekranı (yeni ve düzenleme modları) */}
        <Route path="builder/:formId" element={<FormBuilderScreen />} />

        {/* Belirli bir formun gönderilmiş verilerini listeleme ekranı */}
        <Route path="data/:formId" element={<FormDataListScreen />} />

        {/* Son kullanıcının formu doldurduğu ekran */}
        <Route path="fill/:formId" element={<FormFillScreen />} />
        
        {/* Tanımsız bir yola gidilirse ana listeye yönlendir */}
        <Route path="*" element={<Navigate to="/formforgeapi" replace />} />
      </Routes>
    </div>
  );
};

export default FormForgeApiContainer;