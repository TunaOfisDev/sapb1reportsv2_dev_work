// frontend/src/api/salesbudget.js
import axiosInstance from './axiosconfig';

const getSalesBudgets = async () => {
  try {
    const response = await axiosInstance.get('salesbudget/budgets/');
    return response.data.results;  // 'results' anahtarına göre güncelleme
  } catch (error) {
    console.error('Bütçeleri getirirken bir hata oluştu:', error);
    throw error;
  }
};


const fetchHanaSalesBudgetData = async () => {
  try {
    const response = await axiosInstance.get('salesbudget/fetch-hana-data/');
    return response.data.results;
  } catch (error) {
    console.error('HANA bütçe verilerini getirirken bir hata oluştu:', error);
    throw error;
  }
};

const exportSalesBudgetToXLSX = async () => {
  try {
    // responseType 'blob' olarak ayarlanmalıdır ki dosya olarak indirebilelim
    const response = await axiosInstance.get('salesbudget/export-xlsx/', { responseType: 'blob' });
    
    // Blob nesnesi oluştur
    const blob = new Blob([response.data], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' });
    
    // İndirilecek dosyanın URL'sini oluştur
    const url = window.URL.createObjectURL(blob);
    
    // Bir 'a' elementi oluştur ve bu URL ile ilişkilendir
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', 'sales_budget_report.xlsx'); // İndirilecek dosyanın adını ayarla
    
    // Linki tıkla ve dosyayı indir
    document.body.appendChild(link);
    link.click();
    
    // Linki DOM'dan kaldır ve URL nesnesini bellekten sil
    document.body.removeChild(link);
    window.URL.revokeObjectURL(url);
  } catch (error) {
    console.error('Error exporting sales budget to XLSX:', error);
    throw error;
  }
};

const salesbudget = {
  getSalesBudgets,
  fetchHanaSalesBudgetData,
  exportSalesBudgetToXLSX
};

export default salesbudget;