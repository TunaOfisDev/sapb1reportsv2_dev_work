import axiosInstance from './axiosconfig';

const fetchSalesOfferDetails = async () => {
  try {
    const response = await axiosInstance.get('/salesofferdocsum/sales-offer-details/');
    return response.data;
  } catch (error) {
    console.error('Sales Offer Details Fetching Error:', error);
    throw error;
  }
};

const fetchHanaData = async () => {
  try {
    const response = await axiosInstance.get('/salesofferdocsum/fetch-hana-data/');
    return response.data;
  } catch (error) {
    console.error('Fetch HANA Data Error:', error);
    throw error;
  }
};

const fetchSalesOfferDetailByBelgeNo = async (belgeNo) => {
  try {
    const response = await axiosInstance.get(`/salesofferdocsum/sales-offer-detail/${belgeNo}/`);
    return response.data;
  } catch (error) {
    console.error('Sales offer Detail Fetching Error:', error);
    throw error;
  }
};

const fetchDocumentSummaries = async () => {
  try {
    const response = await axiosInstance.get('/salesofferdocsum/document-summaries/');
    return response.data;
  } catch (error) {
    console.error('Document Summaries Fetching Error:', error);
    throw error;
  }
};

const fetchDocumentSummaryByBelgeNo = async (belgeNo) => {
  try {
    const response = await axiosInstance.get(`/salesofferdocsum/document-summary/${belgeNo}/`);
    return response.data;
  } catch (error) {
    console.error('Document Summary Fetching Error:', error);
    throw error;
  }
};

const fetchFilteredDateDocSum = async (filters) => {
  const params = new URLSearchParams({
    belge_tarih_start: filters.belgeTarihStart,
    belge_tarih_end: filters.belgeTarihEnd,
    teslim_tarih_start: filters.teslimTarihStart,
    teslim_tarih_end: filters.teslimTarihEnd
  }).toString();

  try {
    const response = await axiosInstance.get(`/salesofferdocsum/date-filter/?${params}`);
    return response.data;
  } catch (error) {
    console.error('Filtered Document Summaries Fetching Error:', error);
    throw error;
  }
};

// Yeni özet tablolara erişim için fonksiyonlar pivottables
const fetchCustomerMonthlySummary = async () => {
  try {
    const response = await axiosInstance.get('/salesofferdocsum/customer-monthly-summary/');
    return response.data;
  } catch (error) {
    console.error('Customer Monthly Summary Fetching Error:', error);
    throw error;
  }
};

const fetchMonthlySummary = async () => {
  try {
    const response = await axiosInstance.get('/salesofferdocsum/monthly-summary/');
    return response.data;
  } catch (error) {
    console.error('Monthly Summary Fetching Error:', error);
    throw error;
  }
};

const fetchSellerMonthlySummary = async () => {
  try {
    const response = await axiosInstance.get('/salesofferdocsum/seller-monthly-summary/');
    return response.data;
  } catch (error) {
    console.error('Seller Monthly Summary Fetching Error:', error);
    throw error;
  }
};

const salesofferdocsum = {
  fetchSalesOfferDetails,
  fetchHanaData,
  fetchSalesOfferDetailByBelgeNo,
  fetchDocumentSummaries,
  fetchDocumentSummaryByBelgeNo,
  fetchFilteredDateDocSum, 
  fetchCustomerMonthlySummary,  
  fetchMonthlySummary,          
  fetchSellerMonthlySummary,    
};

export default salesofferdocsum;
