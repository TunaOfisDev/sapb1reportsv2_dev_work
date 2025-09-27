// frontend/src/components/LogoCustomerCollection/api/logo_customer_collection.js

import axiosInstance from '../../../api/axiosconfig';

/**
 * Müşteri yaşlandırma özet verilerini getirir.
 * Endpoint: /api/v2/logocustomercollection/summary/
 */
export const fetchCustomerAgingSummary = async () => {
  try {
    const response = await axiosInstance.get('logocustomercollection/summary/');
    return response.data;
  } catch (error) {
    console.error('Müşteri yaşlandırma özet verisi alınamadı:', error);
    throw error;
  }
};

/**
 * Logo DB'den (logodbcon) canlı veri çekerek yaşlandırma tablosunu günceller.
 * Endpoint: /api/v2/logocustomercollection/fetch-logo-data/
 */
export const fetchLogoData = async () => {
  try {
    const response = await axiosInstance.get('logocustomercollection/fetch-logo-data/');
    return response.data;
  } catch (error) {
    console.error('Logo verisi alınamadı:', error);
    throw error;
  }
};

/**
 * Ham verinin en son ne zaman güncellendiğini döner.
 * Endpoint: /api/v2/logocustomercollection/last-updated/
 */
export const fetchLastUpdated = async () => {
  try {
    const response = await axiosInstance.get('logocustomercollection/last-updated/');
    return response.data;
  } catch (error) {
    console.error('Son güncelleme tarihi alınamadı:', error);
    throw error;
  }
};

/**
 * Ortak export objesi
 */
export const logoCustomerCollectionAPI = {
  fetchCustomerAgingSummary,
  fetchLogoData,
  fetchLastUpdated
};
