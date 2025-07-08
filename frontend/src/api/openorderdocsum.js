// frontend/src/api/openorderdocsum.js
import axiosInstance from './axiosconfig';

const fetchOpenOrderDetails = async () => {
  try {
    const response = await axiosInstance.get('/openorderdocsum/open-order-details/');
    return response.data;
  } catch (error) {
    console.error('Open Order Details Fetching Error:', error);
    throw error;
  }
};

const fetchHanaData = async () => {
  try {
    const response = await axiosInstance.get('/openorderdocsum/fetch-hana-data/');
    return response.data;
  } catch (error) {
    console.error('Fetch HANA Data Error:', error);
    throw error;
  }
};

const fetchOpenOrderDetailByBelgeNo = async (belgeNo) => {
  try {
    const response = await axiosInstance.get(`/openorderdocsum/open-order-detail/${belgeNo}/`);
    return response.data;
  } catch (error) {
    console.error('Open Order Detail Fetching Error:', error);
    throw error;
  }
};

const fetchDocumentSummaries = async () => {
  try {
    const response = await axiosInstance.get('/openorderdocsum/document-summaries/');
    return response.data;
  } catch (error) {
    console.error('Document Summaries Fetching Error:', error);
    throw error;
  }
};

const fetchDocumentSummaryByBelgeNo = async (belgeNo) => {
  try {
    const response = await axiosInstance.get(`/openorderdocsum/document-summary/${belgeNo}/`);
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
    const response = await axiosInstance.get(`/openorderdocsum/date-filter/?${params}`);
    return response.data;
  } catch (error) {
    console.error('Filtered Document Summaries Fetching Error:', error);
    throw error;
  }
};

const openorderdocsum = {
  fetchOpenOrderDetails,
  fetchHanaData,
  fetchOpenOrderDetailByBelgeNo,
  fetchDocumentSummaries,
  fetchDocumentSummaryByBelgeNo,
  fetchFilteredDateDocSum, 

};

export default openorderdocsum;