// frontend/src/components/SystemNotebook/api/systemNoteApi.js

import axiosInstance from '../../../api/axiosconfig';

const BASE_PATH = 'systemnotebook/system-notes/';

/**
 * Sistem notlarını listeler (opsiyonel filtrelerle)
 * @param {Object} params - Filtre parametreleri (örn. { source: 'github' })
 */
export const fetchSystemNotes = async (params = {}) => {
  const response = await axiosInstance.get(BASE_PATH, { params });
  return response.data;
};

/**
 * Tek bir sistem notunu getirir
 * @param {number|string} id - Not ID'si
 */
export const getSystemNoteById = async (id) => {
  const response = await axiosInstance.get(`${BASE_PATH}${id}/`);
  return response.data;
};

/**
 * Yeni sistem notu oluşturur
 * @param {Object} data - Not içeriği { title, content, source }
 */
export const createSystemNote = async (data) => {
  const response = await axiosInstance.post(BASE_PATH, data);
  return response.data;
};

/**
 * Mevcut sistem notunu günceller
 * @param {number|string} id - Not ID'si
 * @param {Object} data - Güncellenmiş içerik
 */
export const updateSystemNote = async (id, data) => {
  const response = await axiosInstance.put(`${BASE_PATH}${id}/`, data);
  return response.data;
};

/**
 * Sistem notunu siler
 * @param {number|string} id - Not ID'si
 */
export const deleteSystemNote = async (id) => {
  const response = await axiosInstance.delete(`${BASE_PATH}${id}/`);
  return response.data;
};

/**
 * GitHub'dan commit çekme tetikleyicisi
 */
export const triggerGithubSync = async () => {
  const response = await axiosInstance.post('systemnotebook/github-sync/');
  return response.data;
};

