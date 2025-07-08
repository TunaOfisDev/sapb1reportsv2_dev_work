// frontend/src/api/salesorder.js
import axiosInstance from './axiosconfig';

const fetchLocalData = async () => {
  try {
    const response = await axiosInstance.get('/salesorder/salesorders/');
    return response.data;
  } catch (error) {
    console.error('Local Sales Orders Fetching Error:', error);
    throw error;
  }
};

const fetchInstantData = async () => {
  try {
    const response = await axiosInstance.get('/salesorder/fetch-hana-data/');
    return response.data;
  } catch (error) {
    console.error('Fetch HANA Data Error:', error);
    throw error;
  }
};

const filterSalesOrdersByTime = async (startTime, endTime) => {
  try {
    const response = await axiosInstance.get(`/salesorder/time-filter/?start_time=${startTime}&end_time=${endTime}`);
    return response.data;
  } catch (error) {
    console.error('Filter Sales Orders By Time Error:', error);
    throw error;
  }
};

const filterSalesOrdersBySecondFilter = async (filterCriteria) => {
  try {
    const response = await axiosInstance.get(`/salesorder/second-filter/?criteria=${filterCriteria}`);
    return response.data;
  } catch (error) {
    console.error('Filter Sales Orders By Second Filter Error:', error);
    throw error;
  }
};

const salesorder = {
  fetchLocalData,
  fetchInstantData,
  filterSalesOrdersByTime,
  filterSalesOrdersBySecondFilter,
};

export default salesorder;