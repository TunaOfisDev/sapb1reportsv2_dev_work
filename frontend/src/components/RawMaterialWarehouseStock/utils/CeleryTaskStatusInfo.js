// frontend/src/components/RawMaterialWarehouseStock/utils/CeleryTaskStatusInfo.js
import React from 'react';

const CeleryTaskStatusInfo = ({ status, error }) => {
  const getStatusMessage = () => {
    switch (status) {
      case 'PENDING':
        return 'Görev kuyruğa alındı, işlenmeyi bekliyor...';
      case 'STARTED':
        return 'Görev başlatıldı, işleniyor...';
      case 'RETRY':
        return 'Görev başarısız oldu, yeniden deneniyor...';
      case 'FAILURE':
        return `Görev başarısız oldu: ${error || 'Bilinmeyen bir hata oluştu.'}`;
      case 'SUCCESS':
        return 'Görev başarıyla tamamlandı.';
      case 'REVOKED':
        return 'Görev iptal edildi.';
      case 'IGNORED':
        return 'Görev göz ardı edildi.';
      case 'RECEIVED':
        return 'Görev alındı, işlenmeye başlanacak.';
      default:
        return 'Bilinmeyen görev durumu.';
    }
  };

  return (
    <div className={`task-status-info ${status}`}>
      {getStatusMessage()}
    </div>
  );
};

export default CeleryTaskStatusInfo;

