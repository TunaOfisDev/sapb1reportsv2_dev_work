// path: frontend/src/components/StockCardIntegration/containers/BulkCreateForm.jsx
import { useState } from 'react';
import styles from '../css/BulkCreateForm.module.css';
import useBulkUpload from '../hooks/useBulkUpload';
import useApiStatus from '../hooks/useApiStatus';
import { bulkCreateStockCards } from '../api/stockCardApi';
import PreviewTable from '../views/PreviewTable';
import { validateBulkData } from '../utils/BulkFormValidators';     // ⬅️ validator
import sampleXlsx from '../templates/sample_stockcard_template.xlsx';

const BulkCreateForm = () => {
  const { previewData, fileError, handleFileUpload, resetUpload } = useBulkUpload();
  const { loading, success, error, start, succeed, fail } = useApiStatus();

  const [showPreview, setShowPreview] = useState(false);
  const [validationErrors, setValidationErrors] = useState([]);     // ⬅️ yeni

  /* -----------------------------------------------
   *  Ön-izleme butonu → önce VALIDATE
   * --------------------------------------------- */
  const handlePreviewClick = () => {
    const { isValid, errors: valErrs } = validateBulkData(previewData);
    if (!isValid) {
      setValidationErrors(valErrs);
      fail('Veri hataları giderilmeden ön-izleme yapılamaz.');
      return;
    }
    setValidationErrors([]);
    setShowPreview(true);
  };

  /* SAP’ya gönder */
  const handleSubmit = async () => {
    if (previewData.length === 0) {
      fail('Yüklenmiş veri bulunamadı.');
      return;
    }
    start();
    try {
      await bulkCreateStockCards(previewData);
      succeed('Stok kartları başarıyla gönderildi!');
      resetUpload();
      setShowPreview(false);
    } catch (err) {
      fail(err);
    }
  };

  /* ------------ Ön-izleme ekranı ------------ */
  if (showPreview) {
    return (
      <div className={styles['bulk-create-form']}>
        <h2 className={styles['bulk-create-form__title']}>Ön-İzleme</h2>

        <PreviewTable data={previewData} />

        <div className={styles['bulk-create-form__preview-actions']}>
          <button
            className={styles['bulk-create-form__back-btn']}
            onClick={() => setShowPreview(false)}
          >
            ← Geri
          </button>

          <button
            onClick={handleSubmit}
            disabled={loading}
            className={styles['bulk-create-form__submit']}
          >
            {loading ? 'Gönderiliyor…' :  'SAP ya Gönder'}
          </button>
        </div>

        {success && <p className={styles['bulk-create-form__success']}>{success}</p>}
        {error && <p className={styles['bulk-create-form__error']}>{error}</p>}
      </div>
    );
  }

  /* ------------- Yükleme ekranı ------------- */
  return (
    <div className={styles['bulk-create-form']}>
      <h2 className={styles['bulk-create-form__title']}>Çoklu Stok Kartı Yükleme</h2>

      {/* Örnek şablon */}
      <div className={styles['bulk-create-form__sample-wrapper']}>
        <a href={sampleXlsx} download className={styles['bulk-create-form__sample-link']}>
          📥 Örnek Excel Şablonunu İndir
        </a>
        <span className={styles['bulk-create-form__sample-hint']}>
          Dosyayı indirip başlıkları değiştirmeden kendi verilerinizi girin.
        </span>
      </div>

      {/* Dosya yükleme */}
      <label htmlFor="stockcard-file" className={styles['bulk-create-form__upload']}>
        {previewData.length > 0
          ? 'Yeni dosya seç (var olanı değiştir)'
          : 'Excel dosyasını buraya bırakın ya da tıklayın'}
        <input
          id="stockcard-file"
          type="file"
          accept=".xlsx,.xls"
          onChange={handleFileUpload}
          className={styles['bulk-create-form__input']}
        />
      </label>
      {fileError && <p className={styles['bulk-create-form__error']}>{fileError}</p>}

      {/* Validator hataları */}
      {validationErrors.length > 0 && (
        <div className={styles['bulk-create-form__error-list']}>
          <p><strong>Bulunan Hatalar:</strong></p>
          <ul>
            {validationErrors.map((msg, i) => (
              <li key={i}>{msg}</li>
            ))}
          </ul>
        </div>
      )}

      {/* Ön-izleme butonu */}
      {previewData.length > 0 && (
        <p className={styles['bulk-create-form__preview']}>
          <strong>{previewData.length}</strong> kayıt yüklendi.
          <button
            className={styles['bulk-create-form__preview-btn']}
            onClick={handlePreviewClick}     
          >
            Ön-izle
          </button>
        </p>
      )}

      {success && <p className={styles['bulk-create-form__success']}>{success}</p>}
      {error && <p className={styles['bulk-create-form__error']}>{error}</p>}
    </div>
  );
};

export default BulkCreateForm;
