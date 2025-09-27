// frontend/src/api/logosupplierbalance.js
import axiosInstance from './axiosconfig';

const fetchSupplierBalances = async () => {
  try {
    const response = await axiosInstance.get('/logosupplierbalance/supplier-balance/');
    return response.data;
  } catch (error) {
    console.error('Supplier Balance Fetching Error:', error);
    throw error;
  }
};

const fetchLogoData = async () => {
  try {
    const response = await axiosInstance.get('/logosupplierbalance/fetch-logo-data/');
    return response.data;
  } catch (error) {
    console.error('Fetch LOGO Data Error:', error);
    throw error;
  }
};

const logosupplierbalance = {
  fetchSupplierBalances,
  fetchLogoData,
};

export default logosupplierbalance;

