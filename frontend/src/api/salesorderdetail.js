// frontend/src/api/salesorderdetail.js
import axiosInstance from './axiosconfig';

const fetchSalesOrderMasters = async () => {
  try {
    const response = await axiosInstance.get('/salesorderdetail/master/');
    return response.data;
  } catch (error) {
    console.error('Sales Order Masters Fetching Error:', error);
    throw error;
  }
};

const fetchSalesOrderMaster = async (id) => {
  try {
    const response = await axiosInstance.get(`/salesorderdetail/master/${id}/`);
    return response.data;
  } catch (error) {
    console.error('Sales Order Master Fetching Error:', error);
    throw error;
  }
};

const fetchSalesOrderDetails = async () => {
  try {
    const response = await axiosInstance.get('/salesorderdetail/detail/');
    return response.data;
  } catch (error) {
    console.error('Sales Order Details Fetching Error:', error);
    throw error;
  }
};

const fetchSalesOrderDetail = async (id) => {
  try {
    const response = await axiosInstance.get(`/salesorderdetail/detail/${id}/`);
    return response.data;
  } catch (error) {
    console.error('Sales Order Detail Fetching Error:', error);
    throw error;
  }
};

const fetchHanaSalesOrderData = async () => {
  try {
    const response = await axiosInstance.get('/salesorderdetail/fetch-sales-order-data/');
    return response.data;
  } catch (error) {
    console.error('Fetch HANA Sales Order Data Error:', error);
    throw error;
  }
};


const fetchSalesOrderDetailsByMasterBelgeGirisNo = async (masterBelgeGirisNo) => {
  try {
    const response = await axiosInstance.get(`/salesorderdetail/detail/search/?master_belge_giris_no=${masterBelgeGirisNo}`);
    return response.data;
  } catch (error) {
    console.error('Sales Order Details Fetching By MasterBelgeGirisNo Error:', error);
    throw error;
  }
};

const salesorderdetail = {
  fetchSalesOrderMasters,
  fetchSalesOrderMaster,
  fetchSalesOrderDetails,
  fetchSalesOrderDetail,
  fetchHanaSalesOrderData,
  fetchSalesOrderDetailsByMasterBelgeGirisNo,
};

export default salesorderdetail;