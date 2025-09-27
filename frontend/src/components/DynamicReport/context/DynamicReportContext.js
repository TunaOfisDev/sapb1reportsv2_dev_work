// frontend/src/components/DynamicReport/context/DynamicReportContext.js
import React, { createContext, useContext, useState } from 'react';

// Yeni bir Context oluştur
export const DynamicReportContext = createContext();

// Provider component'ı
export const DynamicReportProvider = ({ children }) => {
    const [manualHeaders, setManualHeaders] = useState(null);
    const [selectedTableName, setSelectedTableName] = useState(null);

    return (
        <DynamicReportContext.Provider value={{ manualHeaders, setManualHeaders, selectedTableName, setSelectedTableName }}>
            {children}
        </DynamicReportContext.Provider>
    );
};

// Custom Hook for using DynamicReport Context
export const useDynamicReportContext = () => {
    return useContext(DynamicReportContext);
};
