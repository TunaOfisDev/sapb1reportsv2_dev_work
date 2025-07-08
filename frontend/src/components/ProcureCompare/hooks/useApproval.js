// frontend/src/components/ProcureCompare/hooks/useApproval.js

import { useState } from 'react';
import axios from '../../../api/axiosconfig';

/**
 * Satınalma onay ve iptal işlemleri için özel hook
 */
const useApproval = () => {
  const [approvalLoading, setApprovalLoading] = useState(false);
  const [approvalError, setApprovalError] = useState(null);
  const [approvalSuccess, setApprovalSuccess] = useState(false);

  const validatePayload = (payload) => {
    if (!payload.belge_no || !payload.uniq_detail_no) {
      throw new Error('Belge No ve Uniq Detail No zorunludur.');
    }
  };

  /**
   * Onay veya Red işlemi gönderir
   * @param {Object} payload - gönderilecek onay form verisi
   */
  const submitApproval = async (payload) => {
    setApprovalLoading(true);
    setApprovalError(null);
    setApprovalSuccess(false);

    try {
      validatePayload(payload);
      console.log('[Onay Gönderiliyor]', payload);

      const response = await axios.post('procure_compare/approval-action/', payload);

      setApprovalSuccess(true);
      return response.data;
    } catch (error) {
      console.error('[Onay Hatası]', error);
      const errMsg =
        error?.response?.data?.error ||
        error?.message ||
        'Onay işlemi sırasında beklenmeyen bir hata oluştu.';
      setApprovalError(errMsg);
      throw new Error(errMsg);
    } finally {
      setApprovalLoading(false);
    }
  };

  /**
   * Onay iptal işlemi gönderir
   * @param {Object} payload - iptal edilecek onaya ait veriler
   */
  const submitApprovalCancel = async (payload) => {
    setApprovalLoading(true);
    setApprovalError(null);
    setApprovalSuccess(false);

    try {
      validatePayload(payload);
      const cancelPayload = { ...payload, action: 'onay_iptal' };
      console.log('[Onay İptal Gönderiliyor]', cancelPayload);

      const response = await axios.post('procure_compare/approval-action/', cancelPayload);

      setApprovalSuccess(true);
      return response.data;
    } catch (error) {
      console.error('[Onay İptal Hatası]', error);
      const errMsg =
        error?.response?.data?.error ||
        error?.message ||
        'Onay iptal işlemi sırasında hata oluştu.';
      setApprovalError(errMsg);
      throw new Error(errMsg);
    } finally {
      setApprovalLoading(false);
    }
  };

  return {
    submitApproval,
    submitApprovalCancel,
    approvalLoading,
    approvalError,
    approvalSuccess,
  };
};

export default useApproval;
