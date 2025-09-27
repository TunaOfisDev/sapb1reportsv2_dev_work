// path: frontend/src/components/StockCardIntegration/containers/StockCardForm.jsx
import { Controller } from 'react-hook-form';
import styles from '../css/StockCardForm.module.css';
import useApiStatus from '../hooks/useApiStatus';
import { createStockCard } from '../api/stockCardApi';
import { getItemGroupOptions } from '../utils/itemGroupLabels';
import CurrencyInput from './CurrencyInput';
import useStockCardForm from '../hooks/useStockCardForm';   // ✅ Yup + RHF entegrasyonu

export default function StockCardForm() {
  /* ------------------------------------------------------------------
   *  Yup şemalı React-Hook-Form nesnesi
   * ---------------------------------------------------------------- */
  const {
    control,
    register,
    handleSubmit,
    formState: { errors },
    reset,
  } = useStockCardForm();      // ← yupResolver burada devrede

  const { loading, success, error, start, succeed, fail } = useApiStatus();

  /* ------------------------------------------------------------------
   *  Submit işlemi
   * ---------------------------------------------------------------- */
  const onSubmit = async (data) => {
    start();
    try {
      const payload = {
        ...data,
        Price: Number(data.Price) || 0,
      };
      await createStockCard(payload);
      succeed('Stok kartı başarıyla gönderildi!');
      reset();                                  // 🔄 formu temizle
    } catch (err) {
      fail(err.message || 'Stok kartı gönderilirken hata oluştu.');
    }
  };

  /*  Form genel kilit kontrolü  */
  const fieldDisabled = loading;

  return (
    <form onSubmit={handleSubmit(onSubmit)} className={styles['stock-card-form']}>
      <h2 className={styles['stock-card-form__title']}>Stok Kartı Oluştur</h2>

      {/* ---------------- Form Grid ---------------- */}
      <div className={styles['stock-card-form__grid']}>

        {/* itemCode */}
        <div className={styles['stock-card-form__field']} style={{ gridColumn: 'span 2' }}>
          <label className={styles['stock-card-form__label']}>Kalem Kodu</label>
          <input
            {...register('itemCode')}                /* Yup kontrolünde */
            maxLength={50}
            className={`${styles['stock-card-form__input']} ${styles['item-code']}`}
            disabled={fieldDisabled}
          />
          {errors.itemCode && (
            <p className={styles['stock-card-form__error']}>{errors.itemCode.message}</p>
          )}
        </div>

        {/* itemName */}
        <div className={styles['stock-card-form__field']} style={{ gridColumn: 'span 2' }}>
          <label className={styles['stock-card-form__label']}>Kalem Tanımı</label>
          <textarea
            {...register('itemName')}
            rows={3}
            maxLength={200}
            className={`${styles['stock-card-form__input']} ${styles['item-name']}`}
            disabled={fieldDisabled}
          />
          {errors.itemName && (
            <p className={styles['stock-card-form__error']}>{errors.itemName.message}</p>
          )}
        </div>

        {/* SalesUnit */}
        <div className={styles['stock-card-form__field']}>
          <label className={styles['stock-card-form__label']}>Satış Ölçü Birimi</label>
          <input
            {...register('SalesUnit')}
            value="Ad"
            readOnly
            className={styles['stock-card-form__input']}
          />
        </div>

        {/* ItemsGroupCode */}
        <div className={styles['stock-card-form__field']}>
          <label className={styles['stock-card-form__label']}>Ürün Grubu</label>
          <select
            {...register('ItemsGroupCode')}
            className={styles['stock-card-form__input']}
            disabled={fieldDisabled}
          >
            <option value="">Seçiniz</option>
            {getItemGroupOptions().map((opt) => (
              <option key={opt.value} value={opt.value}>
                {opt.label}
              </option>
            ))}
          </select>
          {errors.ItemsGroupCode && (
            <p className={styles['stock-card-form__error']}>{errors.ItemsGroupCode.message}</p>
          )}
        </div>

        {/* SalesVATGroup */}
        <div className={styles['stock-card-form__field']}>
          <label className={styles['stock-card-form__label']}>KDV Grubu</label>
          <select
            {...register('SalesVATGroup')}
            className={styles['stock-card-form__input']}
            disabled={fieldDisabled}
          >
            <option value="HES0010">KDV %10</option>
            <option value="HES0020">KDV %20</option>
          </select>
          {errors.SalesVATGroup && (
            <p className={styles['stock-card-form__error']}>{errors.SalesVATGroup.message}</p>
          )}
        </div>

        {/* Price */}
        <div className={styles['stock-card-form__field']}>
          <label className={styles['stock-card-form__label']}>Fiyat</label>
          <Controller
            name="Price"
            control={control}
            rules={{
              /* Ek ondalık /digit kontrolü – Yup’taki pozitif sayı kuralına ek */
              validate: (value) => {
                if (value === '' || value === null) return 'Fiyat alanı zorunludur.';
                if (isNaN(value) || value < 0) return 'Lütfen geçerli bir fiyat giriniz.';
                if (value > 9999999999.9999)
                  return 'Maksimum 10 tam ve 4 ondalık hane olabilir.';
                return true;
              },
            }}
            render={({ field }) => (
              <CurrencyInput
                {...field}
                decimalPlaces={4}
                placeholder="0,0000"
                className={styles['stock-card-form__input']}
                style={{ textAlign: 'right' }}
                disabled={fieldDisabled}
              />
            )}
          />
          {errors.Price && (
            <p className={styles['stock-card-form__error']}>{errors.Price.message}</p>
          )}
        </div>

        {/* Currency */}
        <div className={styles['stock-card-form__field']}>
          <label className={styles['stock-card-form__label']}>Para Birimi</label>
          <select
            {...register('Currency')}
            className={styles['stock-card-form__input']}
            disabled={fieldDisabled}
          >
            <option value="EUR">EUR</option>
            <option value="USD">USD</option>
            <option value="TRY">TRY</option>
            <option value="GBP">GBP</option>
          </select>
          {errors.Currency && (
            <p className={styles['stock-card-form__error']}>{errors.Currency.message}</p>
          )}
        </div>

        {/* U_eski_bilesen_kod */}
        <div className={styles['stock-card-form__field']}>
          <label className={styles['stock-card-form__label']}>Eski Bileşen Kod</label>
          <input
            {...register('U_eski_bilesen_kod')}
            className={styles['stock-card-form__input']}
            disabled={fieldDisabled}
          />
        </div>
      </div>

      {/* ---------------- Submit & Durum Mesajları ---------------- */}
      <button
        type="submit"
        className={styles['stock-card-form__submit']}
        disabled={loading}
      >
        {loading ? 'Gönderiliyor…' : 'SAP’ya Gönder'}
      </button>

      {success && <p className={styles['stock-card-form__success']}>{success}</p>}
      {error && <p className={styles['stock-card-form__error']}>{error}</p>}
    </form>
  );
}
