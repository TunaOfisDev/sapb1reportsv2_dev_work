// path: frontend/src/components/StockCardIntegration/containers/UpdateForm.jsx
import { useState } from 'react';
import styles from '../css/UpdateForm.module.css';
import {
  updateStockCardByCode,
  fetchLiveSAPStockCardByCode,
} from '../api/stockCardApi';
import useApiStatus from '../hooks/useApiStatus';

/* Yardımcı – 890.99 → "890,99" */
const dotToComma = (val) =>
  typeof val === 'number'
    ? val.toString().replace('.', ',')
    : (val || '').toString().replace('.', ',');

/* Yardımcı – "890,99" → 890.99 */
const commaToDotNumber = (val) =>
  Number((val || '').toString().replace(',', '.'));

const UpdateForm = () => {
  const [formData, setFormData] = useState({
    itemCode: '',
    itemName: '',
    ItemsGroupCode: '',
    SalesVATGroup: '',
    Price: '',
    Currency: '',
    U_eski_bilesen_kod: '',
  });

  const { loading, success, error, start, succeed, fail } = useApiStatus();

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  /* SAP’den canlı detay çek */
  const handleFetchDetails = async () => {
    const itemCode = formData.itemCode.trim();
    if (!itemCode) {
      fail('ItemCode girmelisiniz.');
      return;
    }

    start();
    try {
      const result = await fetchLiveSAPStockCardByCode(itemCode);
      setFormData((prev) => ({
        ...prev,
        itemName: result.ItemName || '',
        ItemsGroupCode: result.ItemsGroupCode?.toString() || '',
        SalesVATGroup: result.SalesVATGroup || '',
        Price: dotToComma(result.ItemPrices?.[0]?.Price ?? ''),
        Currency: result.ItemPrices?.[0]?.Currency || '',
        U_eski_bilesen_kod: result.U_eski_bilesen_kod || '',
      }));
      succeed('SAP verisi yüklendi.');
    } catch (err) {
      fail('SAP verisi alınamadı.');
    }
  };

  /* Güncelle gönder */
  const handleSubmit = async (e) => {
    e.preventDefault();
    const { itemCode, ...updateData } = formData;

    if (!itemCode) {
      fail('ItemCode boş olamaz.');
      return;
    }

    start();
    try {
      const payload = {
        ...updateData,
        /* backend sayı bekler */
        Price: commaToDotNumber(updateData.Price),
        ItemsGroupCode: Number(updateData.ItemsGroupCode || 0),
      };
      await updateStockCardByCode(itemCode, payload);
      succeed('Stok kartı başarıyla güncellendi.');
    } catch (err) {
      fail(err);
    }
  };

  return (
    <form className={styles['update-form']} onSubmit={handleSubmit}>
      <h2 className={styles['update-form__title']}>Stok Kartı Güncelle</h2>

      <div className={styles['update-form__grid']}>
        {/* Kalem Kodu */}
        <div className={styles['update-form__field']} style={{ gridColumn: 'span 2' }}>
          <label className={styles['update-form__label']}>Kalem Kodu</label>
          <input
            name="itemCode"
            value={formData.itemCode}
            onChange={handleChange}
            className={styles['update-form__input']}
            required
          />
        </div>

        {/* Detayı Getir butonu */}
        <div className={styles['update-form__field']}>
          {loading && (
            <p className={styles['update-form__info']}>
              SAP den veri alınıyor, lütfen bekleyin...
            </p>
          )}
          <button
            type="button"
            onClick={handleFetchDetails}
            className={styles['update-form__submit']}
            disabled={loading}
          >
            {loading ? 'Detaylar getiriliyor...' : 'Detayları Getir'}
          </button>
        </div>

        {/* Kalem Tanımı */}
        <div className={styles['update-form__field']} style={{ gridColumn: 'span 2' }}>
          <label className={styles['update-form__label']}>Kalem Tanımı</label>
          <textarea
            name="itemName"
            rows={3}
            value={formData.itemName}
            onChange={handleChange}
            className={styles['update-form__input']}
          />
        </div>

        {/* Ürün Grubu */}
        <div className={styles['update-form__field']}>
          <label className={styles['update-form__label']}>Ürün Grubu</label>
          <select
            name="ItemsGroupCode"
            value={formData.ItemsGroupCode}
            onChange={handleChange}
            className={styles['update-form__input']}
          >
            <option value="">Seçiniz</option>
            <option value="105">Mamul</option>
            <option value="103">Ticari</option>
            <option value="112">Girsberger</option>
          </select>
        </div>

        {/* KDV Grubu */}
        <div className={styles['update-form__field']}>
          <label className={styles['update-form__label']}>KDV Grubu</label>
          <input
            name="SalesVATGroup"
            value={formData.SalesVATGroup}
            onChange={handleChange}
            className={styles['update-form__input']}
          />
        </div>

        {/* Fiyat (virgül destekli) */}
        <div className={styles['update-form__field']}>
          <label className={styles['update-form__label']}>Fiyat</label>
          <input
            type="text"
            name="Price"
            value={formData.Price}
            onChange={handleChange}
            className={styles['update-form__input']}
            placeholder="örn. 1334,99"
          />
        </div>

        {/* Para Birimi */}
        <div className={styles['update-form__field']}>
          <label className={styles['update-form__label']}>Para Birimi</label>
          <select
            name="Currency"
            value={formData.Currency}
            onChange={handleChange}
            className={styles['update-form__input']}
          >
            <option value="">Seçiniz</option>
            <option value="EUR">EUR</option>
            <option value="USD">USD</option>
            <option value="TRY">TRY</option>
            <option value="GBP">GBP</option>
          </select>
        </div>

        {/* Eski Bileşen Kod */}
        <div className={styles['update-form__field']}>
          <label className={styles['update-form__label']}>Eski Bileşen Kod</label>
          <input
            name="U_eski_bilesen_kod"
            value={formData.U_eski_bilesen_kod}
            onChange={handleChange}
            className={styles['update-form__input']}
          />
        </div>
      </div>

      {/* Submit */}
      <button type="submit" className={styles['update-form__submit']} disabled={loading}>
        {loading ? 'Güncelleniyor...' : 'Güncelle'}
      </button>

      {success && <p style={{ color: 'green' }}>{success}</p>}
      {error && <p className={styles['update-form__error']}>{error}</p>}
    </form>
  );
};

export default UpdateForm;
