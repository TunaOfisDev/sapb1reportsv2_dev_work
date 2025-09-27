// frontend/src/components/ProductConfig/utils/pcShowModalVariantDetail.js
import React from 'react';
import { useSelector } from 'react-redux'; // useSelector'ı ekleyelim
import { selectCurrency } from '../store/pcSettingsSlice'; // selectCurrency'yi ekleyelim
import '../css/PCShowModalVariantDetail.css';
import PCModal from '../common/PCModal';
import PCButton from '../common/PCButton';
import { formatPrice } from './pcHelpers';

const statusMap = {
  'draft': 'Taslak',
  'in_progress': 'Devam Ediyor',
  'completed': 'Tamamlandı',
  'archived': 'Arşivlenmiş'
};

const PCShowModalVariantDetail = ({ 
  isOpen, 
  onClose, 
  variant,
  onDeleteClick
}) => {
  // Currency konfigürasyonunu redux'tan alalım
  const currencyConfig = useSelector(selectCurrency);
  
  if (!variant) return null;

  const getStatusBadgeClass = (status) => {
    switch (status) {
      case 'draft':
        return 'pc-variant-status-badge--draft';
      case 'in_progress':
        return 'pc-variant-status-badge--progress';
      case 'completed':
        return 'pc-variant-status-badge--completed';
      case 'archived':
        return 'pc-variant-status-badge--archived';
      default:
        return '';
    }
  };

  const renderVariantCode = (code) => {
    if (!code) return '-';
    const parts = code.split('.');
    return (
      <div className="pc-variant-code-parts">
        {parts.map((part, index) => (
          <span key={index} className="pc-variant-code-part">
            {part}
          </span>
        ))}
      </div>
    );
  };

  return (
    <PCModal
      isOpen={isOpen}
      onClose={onClose}
      title="Varyant Detayları"
      size="large"
    >
      <div className="pc-variant-detail">
        <div className="pc-variant-detail__header">
          <div className="pc-variant-detail__status">
            <span className={`pc-variant-status-badge ${getStatusBadgeClass(variant.status)}`}>
              {statusMap[variant.status] || variant.status}
            </span>
          </div>
        </div>

        <div className="pc-variant-detail__content">
          <div className="pc-variant-detail__section">
            <h3 className="pc-variant-detail__section-title">Proje Bilgileri</h3>
            <div className="pc-variant-detail__field">
              <span className="pc-variant-detail__label">Proje Adı:</span>
              <span className="pc-variant-detail__value">{variant.project_name || '-'}</span>
            </div>
            <div className="pc-variant-detail__field">
              <span className="pc-variant-detail__label">ID:</span>
              <span className="pc-variant-detail__value">{variant.id}</span>
            </div>
          </div>

          <div className="pc-variant-detail__section">
            <h3 className="pc-variant-detail__section-title">Varyant Bilgileri</h3>
            <div className="pc-variant-detail__field">
              <span className="pc-variant-detail__label">Varyant Kodu:</span>
              <div className="pc-variant-detail__value pc-variant-detail__code">
                {renderVariantCode(variant.variant_code)}
              </div>
            </div>
            <div className="pc-variant-detail__field">
              <span className="pc-variant-detail__label">Açıklama:</span>
              <span className="pc-variant-detail__value">{variant.variant_description || '-'}</span>
            </div>
            <div className="pc-variant-detail__field">
              <span className="pc-variant-detail__label">Toplam Fiyat:</span>
              <span className="pc-variant-detail__value pc-variant-detail__price">
                {formatPrice(variant.total_price, currencyConfig)} {/* currencyConfig ekledik */}
              </span>
            </div>
          </div>
        </div>

        <div className="pc-variant-detail__actions">
          <PCButton 
            variant="danger"
            onClick={() => onDeleteClick(variant.id)}
          >
            Sil
          </PCButton>
          <PCButton 
            variant="secondary" 
            onClick={onClose}
          >
            Kapat
          </PCButton>
        </div>
      </div>
    </PCModal>
  );
};

export default PCShowModalVariantDetail;