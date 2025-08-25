// path: frontend/src/components/NexusCore/containers/ConnectionManager/ConnectionForm.jsx
import React, { useState, useEffect } from 'react';
import PropTypes from 'prop-types';
import Button from '../../components/common/Button/Button';
import Input from '../../components/common/Input/Input';
import Select from '../../components/common/Select/Select';
import Textarea from '../../components/common/Textarea/Textarea';

// Farklı veritabanı türleri için JSON şablonları
const dbTemplates = {
  postgresql: JSON.stringify({
    "ENGINE": "django.db.backends.postgresql",
    "NAME": "veritabani_adi",
    "USER": "kullanici_adi",
    "PASSWORD": "sifre",
    "HOST": "localhost",
    "PORT": "5432"
  }, null, 2),
  sql_server: JSON.stringify({
    "ENGINE": "mssql",
    "NAME": "veritabani_adi",
    "USER": "kullanici_adi",
    "PASSWORD": "sifre",
    "HOST": "sunucu_adresi",
    "PORT": "1433",
    "OPTIONS": {
      "driver": "ODBC Driver 17 for SQL Server"
    }
  }, null, 2)
};

const dbOptions = [
  { value: 'postgresql', label: 'PostgreSQL' },
  { value: 'sql_server', label: 'Microsoft SQL Server' },
];

const ConnectionForm = ({ onSubmit, onCancel, initialData = null, isSaving = false }) => {
  const [title, setTitle] = useState('');
  const [dbType, setDbType] = useState('postgresql');
  const [configJson, setConfigJson] = useState(dbTemplates.postgresql);
  const [jsonError, setJsonError] = useState(null);

  // `initialData` prop'u değiştiğinde (yani düzenleme moduna geçildiğinde)
  // formun state'ini bu veriyle doldurur.
  useEffect(() => {
    if (initialData) {
      setTitle(initialData.title || '');
      setDbType(initialData.db_type || 'postgresql');
      setConfigJson(JSON.stringify(initialData.config_json, null, 2) || '');
    } else {
      // Yeni kayıt modunda formu sıfırla ve varsayılan şablonu yükle
      setTitle('');
      setDbType('postgresql');
      setConfigJson(dbTemplates.postgresql);
    }
  }, [initialData]);

  // Kullanıcı JSON alanını değiştirirken anlık olarak doğrulama yapar
  const handleJsonChange = (e) => {
    const jsonString = e.target.value;
    setConfigJson(jsonString);
    try {
      JSON.parse(jsonString);
      setJsonError(null); // Hata yoksa temizle
    } catch (error) {
      setJsonError('Geçersiz JSON formatı.'); // Hata varsa state'i ayarla
    }
  };

  const handleDbTypeChange = (e) => {
    const newType = e.target.value;
    setDbType(newType);
    // Sadece "yeni kayıt" modundaysak şablonu otomatik değiştir
    if (!initialData) {
      setConfigJson(dbTemplates[newType] || '');
    }
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (jsonError) {
      // JSON hatası varsa formu gönderme
      return;
    }
    try {
      const parsedConfig = JSON.parse(configJson);
      onSubmit({ title, db_type: dbType, config_json: parsedConfig });
    } catch (error) {
      setJsonError('Göndermeden önce JSON formatını düzeltin.');
    }
  };

  const isFormValid = title.trim() !== '' && !jsonError;

  return (
    <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
      <Input
        id="connection-title"
        label="Bağlantı Başlığı"
        value={title}
        onChange={(e) => setTitle(e.target.value)}
        placeholder="Örn: Üretim Raporlama Veritabanı"
        required
        disabled={isSaving}
      />

      <Select
        id="db-type"
        label="Veritabanı Türü"
        value={dbType}
        onChange={handleDbTypeChange}
        options={dbOptions}
        disabled={isSaving}
      />

      <Textarea
        id="config-json"
        label="JSON Yapılandırması"
        value={configJson}
        onChange={handleJsonChange}
        rows={12}
        error={jsonError}
        helperText="Veritabanı bağlantı ayarlarını JSON formatında girin."
        style={{ fontFamily: 'monospace', fontSize: '0.9rem' }}
        disabled={isSaving}
      />
      
      <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '10px', marginTop: '10px' }}>
        <Button type="button" variant="secondary" onClick={onCancel} disabled={isSaving}>
          İptal
        </Button>
        <Button type="submit" variant="primary" disabled={!isFormValid || isSaving}>
          {isSaving ? 'Kaydediliyor...' : (initialData ? 'Güncelle' : 'Oluştur')}
        </Button>
      </div>
    </form>
  );
};

ConnectionForm.propTypes = {
  onSubmit: PropTypes.func.isRequired,
  onCancel: PropTypes.func.isRequired,
  initialData: PropTypes.object,
  isSaving: PropTypes.bool,
};

export default ConnectionForm;