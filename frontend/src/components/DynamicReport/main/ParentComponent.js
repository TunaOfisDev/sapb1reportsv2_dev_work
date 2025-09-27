// frontend/src/components/DynamicReport/main/ParentComponent.js
import React from 'react';
import DynamicReportContainer from '../containers/DynamicReportContainer';
import useDynamicReport from '../hooks/useDynamicReport'; 

export const ParentComponent = () => {
    const { manualHeaders,  selectedTableName, triggerFetchData } = useDynamicReport(null); // Custom hook'u kullanıyoruz.

    return (
        <div>
            <React.Suspense fallback={<div>Yükleniyor...</div>}>
            <DynamicReportContainer 
                manualHeaders={manualHeaders || []}  // Bu satırı ekledik
                selectedTableName={selectedTableName}
                triggerFetchData={triggerFetchData}
                />
            
              </React.Suspense>
        </div>
    );
};
