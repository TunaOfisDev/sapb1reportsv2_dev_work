
// path: frontend/src/components/StockCardIntegration/utils/ConfirmDialog.jsx

import '../css/ConfirmDialog.module.css';

const ConfirmDialog = ({ isOpen, title, message, onConfirm, onCancel }) => {
  if (!isOpen) return null;

  return (
    <div className="confirm-dialog__overlay">
      <div className="confirm-dialog">
        <h2 className="confirm-dialog__title">{title || 'Onay Gerekli'}</h2>
        <p className="confirm-dialog__message">{message}</p>
        <div className="confirm-dialog__actions">
          <button className="confirm-dialog__btn confirm-dialog__btn--confirm" onClick={onConfirm}>
            Evet, Gönder
          </button>
          <button className="confirm-dialog__btn confirm-dialog__btn--cancel" onClick={onCancel}>
            Hayır, Düzenle
          </button>
        </div>
      </div>
    </div>
  );
};

export default ConfirmDialog;
