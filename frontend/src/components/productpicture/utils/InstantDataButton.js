// frontend/src/components/productpicture/utils/InstantDataButton.js
import React, { useState } from 'react';
import { usePicturNameValidation } from '../context/Context';
import { fetchCombinedData, fetchLocalData } from '../../../api/picturnamevalidationAPI';
import LoadingSpinner from './LoadingSpinner';  

const InstantDataButton = () => {
  const [loading, setLoading] = useState(false);
  const { addToast, setCombinedData, setLocalData } = usePicturNameValidation();
  
  const handleInstantDataClick = async () => {
    setLoading(true);
    try {
      const newCombinedData = await fetchCombinedData('?force_refresh=true', addToast);
      setCombinedData(newCombinedData);
      
      const newLocalData = await fetchLocalData(addToast);
      setLocalData(newLocalData);
    } catch (error) {
      console.error("An error occurred:", error);
      if (addToast) {
        addToast("Veriler güncellenemedi, lütfen daha sonra tekrar deneyin.");
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <button 
        className={`instant_data_button ${loading ? "instant_data_button--loading" : ""}`} 
        onClick={handleInstantDataClick}
        disabled={loading}  
      >
        <span className="instant_data_button__label">
          {loading ? "Yükleniyor..." : "Anlık Veri"}
        </span>
      </button>
      <LoadingSpinner isLoading={loading} />  
    </div>
  );
};

export default InstantDataButton;