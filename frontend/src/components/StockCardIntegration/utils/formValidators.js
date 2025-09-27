// frontend/src/components/StockCardIntegration/utils/formValidators.js
import * as Yup from 'yup';

// Özel para birimi kuralı
const currencyOptions = ['EUR', 'USD', 'TRY', 'GBP'];
const itemGroupCodes  = [103, 105, 112];
const defaultUom      = 'Adet';

/**
 *  ▸ İzinli karakterler: A-Z, 0-9, ., -, _, /
 *  ▸ BAŞ ve SON: mutlaka harf-rakam; nokta, virgül, +, -, _ vb. O-LA-MAZ
 *      ^[A-Z0-9]...........[A-Z0-9]$
 */
const ITEM_CODE_REGEX = /^[A-Z0-9](?:[A-Z0-9._\/-]*[A-Z0-9])?$/;

export const stockCardValidationSchema = Yup.object().shape({
  itemCode: Yup.string()
    .required('Kalem kodu zorunludur')
    .max(50, 'En fazla 50 karakter olabilir')
    .matches(
      ITEM_CODE_REGEX,
      'Kod, büyük harf veya rakamla başlayıp bitmeli; içeride ., -, _, / kullanılabilir'
    ),

  itemName: Yup.string()
    .required('Kalem adı zorunludur')
    .max(200, 'En fazla 200 karakter olabilir'),

  ItemsGroupCode: Yup.number()
    .typeError('Lütfen bir ürün grubu seçiniz')
    .oneOf(itemGroupCodes, 'Geçersiz ürün grubu seçimi')
    .required('Ürün grubu zorunludur'),

  UoMGroupEntry: Yup.string()
    .required('Ölçü birim grubu zorunludur'),

  SalesVATGroup: Yup.string()
    .matches(/^HES\d{4}$/, 'Geçersiz satış vergi grubu formatı (örn: HES0010)')
    .required('Satış vergi grubu zorunludur'),

  Price: Yup.number()
    .typeError('Fiyat sayısal olmalıdır')
    .positive('Fiyat 0\'dan büyük olmalıdır')
    .required('Fiyat zorunludur'),

  Currency: Yup.string()
    .oneOf(currencyOptions, 'Geçersiz döviz birimi')
    .required('Döviz birimi zorunludur'),

  U_eski_bilesen_kod: Yup.string()
    .max(250, 'En fazla 250 karakter olabilir')
    .nullable()
});
