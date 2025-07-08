// frontend/src/api/rawmaterialwarehousestock.js
import axiosInstance from './axiosconfig';

// Tüm raw material warehouse stock verilerini getirir
const getRawMaterialWarehouseStocks = async () => {
  try {
    const response = await axiosInstance.get('rawmaterialwarehousestock/list/');
    return response.data;
  } catch (error) {
    console.error('Error fetching raw material warehouse stocks:', error);
    throw error;
  }
};

// HANA DB'den verileri çekmeyi başlatır
const fetchAndUpdateHanaData = async () => {
  try {
    const response = await axiosInstance.get('rawmaterialwarehousestock/fetch-hana-data/');
    return response.data;
  } catch (error) {
    console.error('Error fetching and updating HANA data:', error);
    throw error;
  }
};

// Kalem grup seçimini günceller
const updateItemGroupSelection = async (isHammadde) => {
  try {
    const response = await axiosInstance.post('rawmaterialwarehousestock/update-selection/', { isHammadde });
    return response.data;
  } catch (error) {
    console.error('Error updating item group selection:', error);
    throw error;
  }
};


const updateZeroStockVisibility = async (hideZeroStock) => {
  try {
    const response = await axiosInstance.post('rawmaterialwarehousestock/update-zero-stock-visibility/', { hideZeroStock });
    return response.data;
  } catch (error) {
    console.error('Error updating zero stock visibility:', error);
    throw error;
  }
};

const getFilteredRawMaterialWarehouseStocks = async () => {
  try {
    const response = await axiosInstance.get('rawmaterialwarehousestock/filtered-list/');
    return response.data;
  } catch (error) {
    console.error('Error fetching filtered raw material warehouse stocks:', error);
    throw error;
  }
};

// Sütun filtresine göre verileri dışa aktarır
const exportColumnFilterData = async (columnFilters) => {
  try {
    const response = await axiosInstance.post('rawmaterialwarehousestock/export/column-filter/', { column_filters: columnFilters }, {
      responseType: 'blob'
    });
    return response.data;
  } catch (error) {
    console.error('Sütun filtresine göre veri dışa aktarılırken hata oluştu:', error);
    throw error;
  }
};


export {
  getRawMaterialWarehouseStocks,
  fetchAndUpdateHanaData,
  updateItemGroupSelection,
  updateZeroStockVisibility,
  getFilteredRawMaterialWarehouseStocks,
  exportColumnFilterData,
 
};