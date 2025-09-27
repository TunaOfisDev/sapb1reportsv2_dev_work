// frontend/src/components/ProcureCompare/components/ApprovalButtons.js
import React, { useState, useCallback, useEffect, useRef } from 'react';
import useApproval from '../hooks/useApproval';
import useOutsideClick from '../hooks/useOutsideClick';
import axios from '../../../api/axiosconfig';
import InlineApprovalDescription from '../utils/InlineApprovalDescription';
import '../css/ApprovalButtons.css';
import '../css/InlineApprovalDescription.css';

const ApprovalButtons = ({ comparisonItem }) => {
  const [selectedAction, setSelectedAction] = useState(null);
  const [activeActionBox, setActiveActionBox] = useState(null);
  const [localError, setLocalError] = useState(null);
  const [localSuccess, setLocalSuccess] = useState(null);
  const [hasPreviousApproval, setHasPreviousApproval] = useState(false);
  const [approvalInfo, setApprovalInfo] = useState(null);

  const {
    submitApproval,
    submitApprovalCancel,
    approvalLoading,
    approvalError
  } = useApproval();

  const isValid = comparisonItem?.uniq_detail_no && comparisonItem?.belge_no;
  const isWarning = comparisonItem?.uyari_var_mi === true;

  // Ref'ler
  const popupRefs = {
    onay: useRef(null),
    kismi_onay: useRef(null),
    red: useRef(null),
    onay_iptal: useRef(null)
  };

  // Dış tıklamaları yakala
  useOutsideClick(popupRefs.onay, () => {
    if (activeActionBox === 'onay') setActiveActionBox(null);
  });
  useOutsideClick(popupRefs.kismi_onay, () => {
    if (activeActionBox === 'kismi_onay') setActiveActionBox(null);
  });
  useOutsideClick(popupRefs.red, () => {
    if (activeActionBox === 'red') setActiveActionBox(null);
  });
  useOutsideClick(popupRefs.onay_iptal, () => {
    if (activeActionBox === 'onay_iptal') setActiveActionBox(null);
  });

  useEffect(() => {
    const fetchApprovalHistory = async () => {
      if (!isValid) return;
      try {
        const res = await axios.get(`procure_compare/approval-history/`, {
          params: {
            belge_no: comparisonItem.belge_no,
            uniq_detail_no: comparisonItem.uniq_detail_no
          }
        });

        const history = res.data?.results?.filter(item =>
          item.belge_no === comparisonItem.belge_no &&
          item.uniq_detail_no === comparisonItem.uniq_detail_no
        );

        if (!history?.length) {
          setHasPreviousApproval(false);
          setApprovalInfo(null);
          return;
        }

        const lastAction = history.sort(
          (a, b) => new Date(b.created_at) - new Date(a.created_at)
        )[0];

        const isFinalApproval = ['onay', 'kismi_onay', 'red'].includes(lastAction.action);

        setHasPreviousApproval(isFinalApproval);
        setApprovalInfo({
          user: lastAction.kullanici_email || 'Bilinmeyen kullanıcı',
          date: lastAction.created_at || 'Tarih yok',
          action: lastAction.action
        });
      } catch (error) {
        console.warn('Onay geçmişi alınamadı:', error);
        setHasPreviousApproval(false);
        setApprovalInfo(null);
      }
    };

    fetchApprovalHistory();
  }, [comparisonItem, isValid]);

  const handleActionClick = useCallback((action) => {
    setSelectedAction(action);
    setActiveActionBox(action);
    setLocalError(null);
    setLocalSuccess(null);
  }, []);

  const handleSubmit = useCallback(async (description) => {
    const payload = {
      belge_no: comparisonItem.belge_no,
      uniq_detail_no: comparisonItem.uniq_detail_no,
      aciklama: description,
      satir_detay_json: comparisonItem
    };

    try {
      if (selectedAction === 'onay_iptal') {
        await submitApprovalCancel(payload);
      } else {
        await submitApproval({ ...payload, action: selectedAction });
      }
      setLocalSuccess('✅ İşleminiz başarıyla tamamlandı.');
    } catch (err) {
      console.error('Onay işlemi hatası:', err);
      setLocalError(err.message || 'Onay işlemi sırasında hata oluştu.');
    } finally {
      setActiveActionBox(null);
      setSelectedAction(null);
    }
  }, [comparisonItem, selectedAction, submitApproval, submitApprovalCancel]);

  const approvalTooltip = approvalInfo
    ? `${approvalInfo.user} tarafından ${approvalInfo.date} tarihinde "${approvalInfo.action.toUpperCase()}" işlemi yapılmış.`
    : "Bu işlem için daha önce onay işlemi yapılmış.";

  const renderButtonWithBox = (label, cssClass, actionType, disabled = false) => (
    <div className="inline-approval-description-wrapper">
      <button
        className={`btn ${cssClass}`}
        onClick={(e) => {
          e.stopPropagation();
          handleActionClick(actionType);
        }}
        disabled={approvalLoading || disabled}
        title={disabled ? approvalTooltip : ""}
      >
        {label}
      </button>

      {activeActionBox === actionType && (
        <div ref={popupRefs[actionType]} className="inline-approval-description-popup">
          <InlineApprovalDescription
            onCancel={() => setActiveActionBox(null)}
            onSubmit={handleSubmit}
          />
        </div>
      )}
    </div>
  );

  useEffect(() => {
    if (approvalError || localError || localSuccess) {
      const timer = setTimeout(() => {
        setLocalError(null);
        setLocalSuccess(null);
      }, 3000);
      return () => clearTimeout(timer);
    }
  }, [approvalError, localError, localSuccess]);

  if (!isValid || isWarning) return null;

  return (
    <div className="approval-buttons-container">
      {(approvalError || localError) && (
        <div className="approval-warning">
          ❌ {approvalError || localError}
        </div>
      )}
      {localSuccess && (
        <div className="approval-success">
          {localSuccess}
        </div>
      )}

      {renderButtonWithBox('Onayla', 'btn-onay', 'onay', hasPreviousApproval)}
      {renderButtonWithBox('Kısmi Onay', 'btn-kismi', 'kismi_onay', hasPreviousApproval)}
      {renderButtonWithBox('Reddet', 'btn-red', 'red', hasPreviousApproval)}
      {renderButtonWithBox('Onay İptali', 'btn-iptal', 'onay_iptal', !hasPreviousApproval)}
    </div>
  );
};

export default ApprovalButtons;
