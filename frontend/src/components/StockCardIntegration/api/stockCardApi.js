// path: frontend/src/components/StockCardIntegration/api/stockCardApi.js
import axiosInstance from '../../../api/axiosconfig';

const BASE_PATH = 'stockcardintegration/stock-cards/';

/* -------------------------------------------------------
 * Excel → Backend eşleme tabloları
 * ----------------------------------------------------- */
const GROUP_MAP = {
  Mamul: 105,
  Ticari: 103,
  Girsberger: 112,
};

const VAT_MAP = {
  'KDV %0':  'EXEMPT',   // örnek: istisna kodu
  'KDV %1':  'HES0001',
  'KDV %8':  'HES0008',
  'KDV %10': 'HES0010',
  'KDV %18': 'HES0018',
};

/* Yardımcı: “890,99” → 890.99 */
const parsePrice = (value) => {
  if (typeof value === 'string') return Number(value.replace(',', '.'));
  return Number(value || 0);
};

/* -------------------------------------------------------
 * DRF serializer’a uygun payload hazırlayıcı
 * ----------------------------------------------------- */
const mapToBackendPayload = (
  formData,
  includeItemCode = false,
  itemCodeParam = null,
) => {
  /* item_code Excel’de “Kalem Kodu” başlığıyla geldiyse yakala */
  const itemCodeToUse =
    itemCodeParam ||
    formData.itemCode ||
    formData['Kalem Kodu'];

  if (includeItemCode && (!itemCodeToUse || String(itemCodeToUse).trim() === '')) {
    console.warn('item_code eksik! mapToBackendPayload iptal edildi.');
    throw new Error('item_code boş olamaz!');
  }

  const payload = {
    item_name:
      formData.itemName ||
      formData['Kalem Tanımı'] ||
      '',

    items_group_code:
      Number(formData.ItemsGroupCode) ||
      GROUP_MAP[formData['Ürün Grubu']] ||
      0,

    price: parsePrice(formData.Price || formData['Fiyat']),

    currency:
      formData.Currency ||
      formData['Para Birimi'] ||
      '',

    U_eski_bilesen_kod:
      formData.U_eski_bilesen_kod ||
      formData['Eski Bileşen Kod'] ||
      '',

    SalesVATGroup:
      formData.SalesVATGroup ||
      VAT_MAP[formData['KDV Grubu']] ||
      '',
  };

  if (includeItemCode) {
    payload.item_code = String(itemCodeToUse);
  }
  return payload;
};

/* -------------------------------------------------------
 *  API çağrıları
 * ----------------------------------------------------- */

// Tekil stok kartı oluştur
export const createStockCard = async (formData) => {
  const payload = mapToBackendPayload(formData, true);
  const response = await axiosInstance.post(BASE_PATH, payload);
  return response.data;
};

// Çoklu stok kartı oluştur
export const bulkCreateStockCards = async (formList) => {
  /* bulk’ta item_code zorunlu ⇒ includeItemCode = true */
  const payloadList = formList.map((row) => mapToBackendPayload(row, true));
  const response = await axiosInstance.post(`${BASE_PATH}bulk-create/`, payloadList);
  return response.data;
};

// Mevcut stok kartını güncelle
export const updateStockCardByCode = async (itemCode, formData) => {
  const payload = mapToBackendPayload(formData, true, itemCode);
  console.log('Güncelleme Payload SAP\'ye gitmeden önce:', payload);
  const response = await axiosInstance.put(
    `${BASE_PATH}code/${encodeURIComponent(itemCode)}/`,
    payload,
  );
  return response.data;
};

// SAP Business One HANA'dan canlı stok kartı getir
export const fetchLiveSAPStockCardByCode = async (itemCode) => {
  const response = await axiosInstance.get(
    `${BASE_PATH}sap-live/${encodeURIComponent(itemCode)}/`,
  );
  return response.data;
};

// Detaylı getir (by item_code)
export const fetchStockCardByCode = async (itemCode) => {
  const response = await axiosInstance.get(
    `${BASE_PATH}code/${encodeURIComponent(itemCode)}/`,
  );
  return response.data;
};

// Listeleme
export const fetchStockCards = async (params = {}) => {
  const response = await axiosInstance.get(BASE_PATH, { params });
  return response.data;
};

// Detaylı getir (by primary key id)
export const fetchStockCardById = async (id) => {
  const response = await axiosInstance.get(`${BASE_PATH}${id}/`);
  return response.data;
};

// SAP senkronizasyonunu tetikle (manuel)
export const triggerSyncStockCard = async (id) => {
  const response = await axiosInstance.post(`${BASE_PATH}${id}/trigger-sync/`);
  return response.data;
};

// Yardım metinlerini getir
export const fetchFieldHelpTexts = async () => {
  const response = await axiosInstance.get('stockcardintegration/field-help-texts/');
  return response.data;
};
