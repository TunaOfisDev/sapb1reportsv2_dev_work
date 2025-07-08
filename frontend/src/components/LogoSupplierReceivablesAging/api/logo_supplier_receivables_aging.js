// frontend/src/components/logo_supplier_receivables_aging/api/logo_supplier_receivables_aging.js

import axiosInstance from '../../../api/axiosconfig';

/**
 * Tedarikçi yaşlandırma özet verilerini getirir.
 */
export const fetchSupplierAgingSummary = async () => {
  try {
    const response = await axiosInstance.get('logo_supplier_receivables_aging/summary/');
    return response.data;
  } catch (error) {
    console.error('Yaşlandırma özet verisi alınamadı:', error);
    throw error;
  }
};

/**
 * HANA'dan canlı veri çekerek sistemdeki tabloyu günceller.
 */
export const fetchHanaData = async () => {
  try {
    const response = await axiosInstance.get('logo_supplier_receivables_aging/fetch-hana-data/');
    return response.data;
  } catch (error) {
    console.error('HANA verisi alınamadı:', error);
    throw error;
  }
};

/**
 * Ham verinin en son ne zaman güncellendiğini döner.
 */
export const fetchLastUpdated = async () => {
  try {
    const response = await axiosInstance.get('logo_supplier_receivables_aging/last-updated/');
    return response.data;
  } catch (error) {
    console.error('Son güncelleme tarihi alınamadı:', error);
    throw error;
  }
};

export const logoSupplierReceivablesAgingAPI = {
  fetchSupplierAgingSummary,
  fetchHanaData,
  fetchLastUpdated
};
