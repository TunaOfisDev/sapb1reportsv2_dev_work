// frontend/src/api/logocustomerbalance.js
import axiosInstance from './axiosconfig';

const fetchCustomerBalances = async () => {
  try {
    const response = await axiosInstance.get('/logocustomerbalance/customer-balance/');
    return response.data;
  } catch (error) {
    console.error('Customer Balance Fetching Error:', error);
    throw error;
  }
};

const fetchLogoData = async () => {
  try {
    const response = await axiosInstance.get('/logocustomerbalance/fetch-logo-data/');
    return response.data;
  } catch (error) {
    console.error('Fetch LOGO Data Error:', error);
    throw error;
  }
};

const logocustomerbalance = {
  fetchCustomerBalances,
  fetchLogoData,
};

export default logocustomerbalance;

