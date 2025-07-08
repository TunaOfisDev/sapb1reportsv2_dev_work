// frontend/src/components/SalesBudgetEur/api/salesbudgeteurApi.js

import axiosInstance from '../../../api/axiosconfig';

// 📥 1. Local DB'den EUR bazlı satış bütçesi verilerini getir
export const fetchSalesBudgetEUR = async () => {
  const response = await axiosInstance.get('salesbudgeteur/budgets-eur/');
  return response.data;
};

// 🔄 2. HANA DB'den canlı veri çek ve backend'e kaydet
export const fetchSalesBudgetFromHana = async () => {
  const response = await axiosInstance.post('salesbudgeteur/fetch-hana-data/');
  return response.data;
};

// 📤 3. Excel formatında veriyi indir
export const exportSalesBudgetEURToExcel = async () => {
  const response = await axiosInstance.get('salesbudgeteur/export-xlsx/', {
    responseType: 'blob' // Excel dosyası için binary veri tipi
  });
  return response;
};
