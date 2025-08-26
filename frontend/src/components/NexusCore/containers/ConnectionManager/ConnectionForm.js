// path: frontend/src/components/NexusCore/containers/ConnectionManager/ConnectionForm.jsx
import React, { useState, useEffect } from 'react';
import PropTypes from 'prop-types';
import Button from '../../components/common/Button/Button';
import Input from '../../components/common/Input/Input';
import Select from '../../components/common/Select/Select';
import Textarea from '../../components/common/Textarea/Textarea';

// ### DEĞİŞİKLİK 1: Popüler veritabanı listemizi import ediyoruz ###
import popularDBList from '../../utils/populardblist';

// Özel olarak bildiğimiz veritabanları için detaylı JSON şablonları
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
  // Gelecekte MongoDB, Oracle vb. için özel şablonlar buraya eklenebilir.
};

// ### DEĞİŞİKLİK 2: Özel şablonumuz olmadığında gösterilecek jenerik bir şablon oluşturuyoruz ###
const genericTemplate = JSON.stringify({
    "ENGINE": "django_engine_path_girin",
    "NAME": "veritabani_adi",
    "USER": "kullanici_adi",
    "PASSWORD": "sifre",
    "HOST": "sunucu_adresi",
    "PORT": "port"
}, null, 2);


// ### DEĞİŞİKLİK 3: Eski, statik dbOptions listesi kaldırıldı ###
// const dbOptions = [ ... ];

const ConnectionForm = ({ onSubmit, onCancel, initialData = null, isSaving = false }) => {
  // Formun başlangıç değerini dinamik listemizin ilk elemanı yapalım
  const [title, setTitle] = useState('');
  const [dbType, setDbType] = useState(popularDBList[0].value);
  const [configJson, setConfigJson] = useState(dbTemplates[popularDBList[0].value] || genericTemplate);
  const [jsonError, setJsonError] = useState(null);

  useEffect(() => {
    if (initialData) {
      setTitle(initialData.title || '');
      // Gelen verinin listede olup olmadığını kontrol et, yoksa varsayılanı kullan
      const initialDbType = popularDBList.some(db => db.value === initialData.db_type) ? initialData.db_type : popularDBList[0].value;
      setDbType(initialDbType);
      setConfigJson(JSON.stringify(initialData.config_json, null, 2) || '');
    } else {
      // Yeni kayıt modunda formu sıfırla
      setTitle('');
      const defaultDbType = popularDBList[0].value;
      setDbType(defaultDbType);
      setConfigJson(dbTemplates[defaultDbType] || genericTemplate);
    }
  }, [initialData]);

  const handleJsonChange = (e) => {
    const jsonString = e.target.value;
    setConfigJson(jsonString);
    try {
      JSON.parse(jsonString);
      setJsonError(null);
    } catch (error) {
      setJsonError('Geçersiz JSON formatı.');
    }
  };

  const handleDbTypeChange = (e) => {
    const newType = e.target.value;
    setDbType(newType);
    // Yeni kayıt modunda, seçilen türe uygun şablonu yükle.
    // Eğer özel şablon yoksa, jenerik şablonu kullan.
    if (!initialData) {
      setConfigJson(dbTemplates[newType] || genericTemplate);
    }
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (jsonError) return;
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

      {/* ### DEĞİŞİKLİK 4: Select bileşenimiz artık dinamik listemizi kullanıyor ### */}
      <Select
        id="db-type"
        label="Veritabanı Türü"
        value={dbType}
        onChange={handleDbTypeChange}
        options={popularDBList}
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