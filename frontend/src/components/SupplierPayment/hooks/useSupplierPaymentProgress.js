// frontend/src/components/SupplierPayment/hooks/useSupplierPaymentProgress.js
import { useState } from 'react';
import supplierPaymentApi from '../../../api/supplierpayment';

const useSupplierPaymentProgress = () => {
  const [progress, setProgress] = useState(null);

  const startTask = async () => {
    try {
      const taskId = await supplierPaymentApi.fetchHanaDbCombinedService();
      const checkProgress = async () => {
        const response = await supplierPaymentApi.getTaskStatus(taskId);
        if (response.state === 'PENDING' || response.state === 'PROGRESS') {
          setProgress(response.progress);
          setTimeout(checkProgress, 1000); // Her saniye kontrol et
        } else if (response.state === 'SUCCESS') {
          setProgress('Tamamlandı');
        } else {
          setProgress(`Hata: ${response.info}`);
        }
      };
      checkProgress();
    } catch (error) {
      setProgress('Başlatma hatası');
    }
  };

  return {
    progress,
    startTask
  };
};

export default useSupplierPaymentProgress;
