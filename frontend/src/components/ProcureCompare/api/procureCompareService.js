// File: frontend/src/components/ProcureCompare/api/procureCompareService.js

import axios from '../../../api/axiosconfig';

/**
 * Tüm siparişleri getirir.
 * GET /procure_compare/orders/
 */
export const fetchOrders = async () => {
  try {
    const response = await axios.get('procure_compare/orders/');
    return response.data;
  } catch (error) {
    console.error('Satınalma siparişleri alınamadı:', error);
    throw error;
  }
};

/**
 * Tüm teklifleri getirir.
 * GET /procure_compare/quotes/
 */
export const fetchQuotes = async () => {
  try {
    const response = await axios.get('procure_compare/quotes/');
    return response.data;
  } catch (error) {
    console.error('Satınalma teklifleri alınamadı:', error);
    throw error;
  }
};

/**
 * Tüm karşılaştırma verilerini getirir.
 * GET /procure_compare/comparisons/
 */
export const fetchComparisons = async () => {
  try {
    const response = await axios.get('procure_compare/comparisons/');
    console.log("Karşılaştırma verisi:", response.data?.results?.[0]); 
    return response.data.results; // dikkat: .results ile listeye erişiyoruz
  } catch (error) {
    console.error('Satınalma karşılaştırmaları alınamadı:', error);
    throw error;
  }
};


/**
 * HANA'dan veri çekip PostgreSQL'e kaydeder.
 * POST /procure_compare/sync-from-hana/
 */
export const syncDataFromHana = async () => {
  try {
    const response = await axios.post('procure_compare/sync-from-hana/');
    return response.data;
  } catch (error) {
    console.error('HANA veri senkronizasyon hatası:', error);
    throw error;
  }
};

/**
 * Onay, kısmi onay veya red işlemi gönderir.
 * POST /procure_compare/approval-action/
 */
export const submitApproval = async (payload) => {
  try {
    const response = await axios.post('procure_compare/approval-action/', payload);
    return response.data;
  } catch (error) {
    console.error('Onay işlemi hatası:', error);
    throw error;
  }
};

/**
 * Onay iptal işlemi gönderir.
 * POST /procure_compare/approval-action/
 */
export const submitApprovalCancel = async (payload) => {
  const cancelPayload = {
    ...payload,
    action: 'onay_iptal'
  };

  try {
    const response = await axios.post('procure_compare/approval-action/', cancelPayload);
    return response.data;
  } catch (error) {
    console.error('Onay iptal işlemi hatası:', error);
    throw error;
  }
};

/**
 * Belirli bir belge ve uniq_detail_no için sıralı onay geçmişini getirir.
 * GET /procure_compare/approval-history-grouped/?belge_no=...&uniq_detail_no=...
 */
export const fetchGroupedApprovalHistory = async (belgeNo, uniqDetailNo) => {
  try {
    const response = await axios.get('procure_compare/approval-history-grouped/', {
      params: {
        belge_no: belgeNo,
        uniq_detail_no: uniqDetailNo
      }
    });
    return response.data?.gecmis || [];
  } catch (error) {
    console.error('Onay geçmişi (gruplu) alınamadı:', error);
    return [];
  }
};

/**
 * Belirli bir ItemCode için son 10 satınalma fiyat geçmişini getirir.
 * GET /api/v2/hanadbcon/query/item_purchase_history/?item_code=...
 */
export const fetchItemPurchaseHistory = async (itemCode) => {
  try {
    const response = await axios.get('procure_compare/item-purchase-history/', {
      params: {
        item_code: itemCode
      }
    });
    return response.data;
  } catch (error) {
    console.error('Satınalma geçmişi alınamadı:', error);
    throw error;
  }
};
