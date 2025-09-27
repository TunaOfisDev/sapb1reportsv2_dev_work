// frontend/src/api/activities.js
import axiosInstance from './axiosconfig';

const fetchLocalData = async () => {
  try {
    const response = await axiosInstance.get('/activities/list/');
    return response.data;
  } catch (error) {
    console.error('Error fetching local activities data:', error);
    throw error;
  }
};

const fetchHanaData = async () => {
  try {
    const response = await axiosInstance.get('/activities/fetch-hana-data/');
    return response.data;
  } catch (error) {
    console.error('Error fetching HANA activities data:', error);
    throw error;
  }
};

const exportActivitiesXLSX = async () => {
  try {
    const response = await axiosInstance.get('/activities/export-activities-xlsx/', {
      responseType: 'blob',
    });
    return response.data;
  } catch (error) {
    console.error('Error exporting activities to XLSX:', error);
    throw error;
  }
};

const activities = {
  fetchLocalData,
  fetchHanaData,
  exportActivitiesXLSX,
};

export default activities;
