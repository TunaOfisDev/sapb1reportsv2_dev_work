// frontend/src/api/salesorderdocsum.js
import axiosInstance from './axiosconfig';

const fetchSalesOrderDetails = async () => {
  try {
    const response = await axiosInstance.get('/salesorderdocsum/sales-order-details/');
    return response.data;
  } catch (error) {
    console.error('Sales Order Details Fetching Error:', error);
    throw error;
  }
};

const fetchHanaData = async () => {
  try {
    const response = await axiosInstance.get('/salesorderdocsum/fetch-hana-data/');
    return response.data;
  } catch (error) {
    console.error('Fetch HANA Data Error:', error);
    throw error;
  }
};

const fetchSalesOrderDetailByBelgeNo = async (belgeNo) => {
  try {
    const response = await axiosInstance.get(`/salesorderdocsum/sales-order-detail/${belgeNo}/`);
    return response.data;
  } catch (error) {
    console.error('Sales Order Detail Fetching Error:', error);
    throw error;
  }
};

const fetchDocumentSummaries = async () => {
  try {
    const response = await axiosInstance.get('/salesorderdocsum/document-summaries/');
    return response.data;
  } catch (error) {
    console.error('Document Summaries Fetching Error:', error);
    throw error;
  }
};

const fetchDocumentSummaryByBelgeNo = async (belgeNo) => {
  try {
    const response = await axiosInstance.get(`/salesorderdocsum/document-summary/${belgeNo}/`);
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
    const response = await axiosInstance.get(`/salesorderdocsum/date-filter/?${params}`);
    return response.data;
  } catch (error) {
    console.error('Filtered Document Summaries Fetching Error:', error);
    throw error;
  }
};

const salesorderdocsum  = {
  fetchSalesOrderDetails,
  fetchHanaData,
  fetchSalesOrderDetailByBelgeNo,
  fetchDocumentSummaries,
  fetchDocumentSummaryByBelgeNo,
  fetchFilteredDateDocSum, 
};

export default salesorderdocsum;



