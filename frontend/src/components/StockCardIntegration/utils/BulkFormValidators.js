// path: frontend/src/components/StockCardIntegration/utils/BulkFormValidators.js

/**
 * 🚦 Bulk Yükleme İçin Satır Doğrulayıcılar
 *
 * Kurallar
 * 1️⃣ Kalem Kodu benzersiz olmalı. (Max 50 karakter, boşluk & Türkçe karakter içermez)
 * 2️⃣ Kalem Tanımı ve Eski Bileşen Kod max 200 karakter olmalı.
 * 3️⃣ Satış Ölçü Birimi **yalnız "Ad"** olabilir.
 * 4️⃣ Ürün Grubu yalnızca **105 (Mamul)**, **103 (Ticari)** veya **112 (Girsberger)** olabilir.
 * 5️⃣ Fiyat "10 tam + 4 ondalık" (virgül ◦ veya nokta) formatında olmalı. Örn: 890,99 – 1234567890,1234
 * 6️⃣ Para Birimi yalnızca EUR, USD, TRY veya GBP olabilir.
 * 7️⃣ KDV Grubu yalnızca **KDV %10** veya **KDV %20** olabilir.
 */

const ALLOWED_CURRENCIES = new Set(['EUR', 'USD', 'TRY', 'GBP']);
const ALLOWED_VAT = new Set(['KDV %10', 'KDV %20']);
const ALLOWED_SALES_UNIT = 'Ad';
const PRICE_REGEX = /^(\d{1,10})([.,]\d{1,4})?$/; // 10 tam + ops. 4 ondalık
const ALLOWED_GROUP_LABELS = {
  'Mamul': 105,
  'Ticari': 103,
  'Girsberger': 112,
};

/**
 * Tek satır doğrulaması
 */
const validateRow = (row, rowIndex, seenItemCodes) => {
  const errs = [];
  const line = rowIndex + 2; // 1. satır başlık

  /* 1️⃣ Kalem Kodu -------------------------------------------------- */
  const itemCode = row['Kalem Kodu']?.trim();
  if (!itemCode) {
    errs.push(`Satır ${line}: Kalem Kodu boş olamaz.`);
  } else {
    if (itemCode.length > 50)
      errs.push(`Satır ${line}: Kalem Kodu 50 karakteri geçemez.`);
    if (/\s|[ĞÜŞİÖÇğüşiöç]/.test(itemCode))
      errs.push(`Satır ${line}: Kalem Kodu boşluk/Türkçe karakter içeremez.`);
    if (seenItemCodes.has(itemCode))
      errs.push(`Satır ${line}: Kalem Kodu "${itemCode}" listede tekrarlanıyor.`);
    else seenItemCodes.add(itemCode);
  }

  /* 2️⃣ Kalem Tanımı ------------------------------------------------ */
  const itemName = row['Kalem Tanımı']?.trim();
  if (!itemName) {
    errs.push(`Satır ${line}: Kalem Tanımı boş olamaz.`);
  } else if (itemName.length > 200) {
    errs.push(`Satır ${line}: Kalem Tanımı 200 karakteri aşamaz.`);
  }

  /* 3️⃣ Eski Bileşen Kod ------------------------------------------- */
  const oldCode = row['Eski Bileşen Kod']?.trim();
  if (oldCode && oldCode.length > 200) {
    errs.push(`Satır ${line}: Eski Bileşen Kod 200 karakteri aşamaz.`);
  }

  /* 4️⃣ Satış Ölçü Birimi ------------------------------------------ */
  const salesUnit = row['Satış Ölçü Birimi']?.trim();
  if (salesUnit && salesUnit !== ALLOWED_SALES_UNIT) {
    errs.push(
      `Satır ${line}: Satış Ölçü Birimi "${salesUnit}" geçersiz (yalnız "${ALLOWED_SALES_UNIT}").`,
    );
  }

  /* 5️⃣ Ürün Grubu -------------------------------------------------- */
  const groupLabel = row['Ürün Grubu']?.trim();
  if (!Object.keys(ALLOWED_GROUP_LABELS).includes(groupLabel)) {
    errs.push(
      `Satır ${line}: Ürün Grubu "${groupLabel}" geçerli değil (yalnız "Mamul", "Ticari", "Girsberger").`,
    );
  }

  /* 6️⃣ Fiyat ------------------------------------------------------- */
  const priceRaw = row['Fiyat']?.toString();
  if (!priceRaw) {
    errs.push(`Satır ${line}: Fiyat boş olamaz.`);
  } else if (!PRICE_REGEX.test(priceRaw)) {
    errs.push(
      `Satır ${line}: Fiyat formatı hatalı (örn. 890,99 veya 1234567890,1234).`,
    );
  }

  /* 7️⃣ Para Birimi ------------------------------------------------- */
  const currency = row['Para Birimi']?.trim();
  if (!ALLOWED_CURRENCIES.has(currency)) {
    errs.push(
      `Satır ${line}: Para Birimi "${currency}" geçerli değil (EUR, USD, TRY, GBP).`,
    );
  }

  /* 8️⃣ KDV Grubu --------------------------------------------------- */
  const vatGroup = row['KDV Grubu']?.trim();
  if (!ALLOWED_VAT.has(vatGroup)) {
    errs.push(
      `Satır ${line}: KDV Grubu "${vatGroup}" geçerli değil (yalnız "KDV %10" veya "KDV %20").`,
    );
  }

  return errs;
};

/**
 * Liste doğrulayıcı
 */
export const validateBulkData = (data = []) => {
  const seenCodes = new Set();
  let errors = [];

  data.forEach((row, idx) => {
    errors = errors.concat(validateRow(row, idx, seenCodes));
  });

  return { isValid: errors.length === 0, errors };
};
