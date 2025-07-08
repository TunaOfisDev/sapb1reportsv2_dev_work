// frontend/src/api/customercollection.js
import axiosInstance from './axiosconfig';

const getLocalDbCustomerCollections = async () => {
  try {
    const response = await axiosInstance.get('customercollection/local_db_closing_invoice/');
    return response.data;
  } catch (error) {
    console.error('Error fetching local DB customer collections:', error);
    throw error;
  }
};

const fetchHanaDbCustomerCollection = async () => {
  try {
    const response = await axiosInstance.get('customercollection/fetch_customer_collection/');
    return response.data;
  } catch (error) {
    console.error('Error fetching HANA DB customer collection data:', error);
    throw error;
  }
};

const getLastUpdatedCustomerCollection = async () => {
  try {
    const response = await axiosInstance.get('customercollection/last_updated_customer_collection/');
    return response.data.last_updated;
  } catch (error) {
    console.error('Error fetching the last updated time:', error);
    throw error;
  }
};


const fetchHanaDbCombinedService = async () => {
  try {
    const response = await axiosInstance.get('customercollection/fetch_hana_db_combined_service/');
    return response.data;
  } catch (error) {
    console.error('Error fetching HANA DB combined service data:', error);
    throw error;
  }
};

const customercollection = {
  getLocalDbCustomerCollections,
  fetchHanaDbCustomerCollection,
  getLastUpdatedCustomerCollection,
  fetchHanaDbCombinedService,
};

export default customercollection;
