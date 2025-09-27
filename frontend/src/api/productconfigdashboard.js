// frontend/src/api/productconfigdashboard.js
import axiosInstance from './axiosconfig';

// Genel CRUD fonksiyonları
const createItem = async (endpoint, data) => {
  try {
    console.log(`Gönderilen veri (${endpoint}):`, data);
    const response = await axiosInstance.post(`productconfiggame/${endpoint}/`, data);
    console.log(`Başarılı yanıt (${endpoint}):`, response.data);
    return response.data;
  } catch (error) {
    console.error(`Hata detayları (${endpoint}):`, error.response?.data || error.message);
    throw error;
  }
};

const getItem = async (endpoint, id) => {
  try {
    const response = await axiosInstance.get(`productconfiggame/${endpoint}/${id}/`);
    return response.data;
  } catch (error) {
    console.error(`Error fetching item at ${endpoint}/${id}:`, error);
    throw error;
  }
};

const updateItem = async (endpoint, id, item) => {
  try {
    const response = await axiosInstance.put(`productconfiggame/${endpoint}/${id}/`, item);
    return response.data;
  } catch (error) {
    console.error(`Error updating item at ${endpoint}/${id}:`, error);
    throw error;
  }
};

const deleteItem = async (endpoint, id) => {
  try {
    await axiosInstance.delete(`productconfiggame/${endpoint}/${id}/`);
  } catch (error) {
    console.error(`Error deleting item at ${endpoint}/${id}:`, error);
    throw error;
  }
};

const listItems = async (endpoint) => {
  try {
    const response = await axiosInstance.get(`productconfiggame/${endpoint}/`);
    // Eğer response.data bir dizi değilse, results anahtarını kontrol edin
    return Array.isArray(response.data) ? response.data : response.data.results;
  } catch (error) {
    console.error(`Error listing items at ${endpoint}:`, error);
    throw error;
  }
};


// Import/Export fonksiyonları
const importData = async (endpoint, file) => {
  const formData = new FormData();
  formData.append('file', file);

  try {
    const response = await axiosInstance.post(`productconfiggame/import_export/${endpoint}/`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    });
    return response.data;
  } catch (error) {
    console.error(`Error importing data for ${endpoint}:`, error);
    throw error;
  }
};

const exportData = async (endpoint) => {
  try {
    const response = await axiosInstance.get(`productconfiggame/import_export/${endpoint}/`, {
      responseType: 'blob'
    });
    const url = window.URL.createObjectURL(new Blob([response.data]));
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', `${endpoint}.xlsx`);
    document.body.appendChild(link);
    link.click();
    return response.data;
  } catch (error) {
    console.error(`Error exporting data for ${endpoint}:`, error);
    throw error;
  }
};

// Brand API
export const createBrand = (brand) => createItem('brands', brand);
export const getBrand = (id) => getItem('brands', id);
export const updateBrand = (id, brand) => updateItem('brands', id, brand);
export const deleteBrand = (id) => deleteItem('brands', id);
export const listBrands = () => listItems('brands');
export const importBrands = (file) => importData('brands', file);
export const exportBrands = () => exportData('brands');

// Category API
export const createCategory = (category) => createItem('categories', category);
export const getCategory = (id) => getItem('categories', id);
export const updateCategory = (id, category) => updateItem('categories', id, category);
export const deleteCategory = (id) => deleteItem('categories', id);
export const listCategories = () => listItems('categories');
export const importCategories = (file) => importData('categories', file);
export const exportCategories = () => exportData('categories');

// ProductGroup API
export const createProductGroup = (productGroup) => createItem('product_groups', productGroup);
export const getProductGroup = (id) => getItem('product_groups', id);
export const updateProductGroup = (id, productGroup) => updateItem('product_groups', id, productGroup);
export const deleteProductGroup = (id) => deleteItem('product_groups', id);
export const listProductGroups = () => listItems('product_groups');
export const importProductGroups = (file) => importData('product_groups', file);
export const exportProductGroups = () => exportData('product_groups');

// ProductModel API
export const createProductModel = (productModel) => createItem('product_models', productModel);
export const getProductModel = (id) => getItem('product_models', id);
export const updateProductModel = (id, productModel) => updateItem('product_models', id, productModel);
export const deleteProductModel = (id) => deleteItem('product_models', id);
export const listProductModels = () => listItems('product_models');
export const importProductModels = (file) => importData('product_models', file);
export const exportProductModels = () => exportData('product_models');

// FeatureOption API
export const createFeatureOption = (featureOption) => createItem('feature_options', featureOption);
export const getFeatureOption = (id) => getItem('feature_options', id);
export const updateFeatureOption = (id, featureOption) => {
  console.log("Updating feature option:", id, featureOption);
  return updateItem('feature_options', id, featureOption);
};
export const deleteFeatureOption = (id) => deleteItem('feature_options', id);
export const listFeatureOptions = () => listItems('feature_options');
export const importFeatureOptions = (file) => importData('feature_options', file);
export const exportFeatureOptions = () => exportData('feature_options');

// Tag API
export const createTag = (tag) => createItem('tags', tag);
export const getTag = (id) => getItem('tags', id);
export const updateTag = (id, tag) => updateItem('tags', id, tag);
export const deleteTag = (id) => deleteItem('tags', id);
export const listTags = () => listItems('tags');
export const importTags = (file) => importData('tags', file);
export const exportTags = () => exportData('tags');

// ProductModelQuestion API
export const createProductModelQuestion = (productModelQuestion) => createItem('product-model-questions', productModelQuestion);
export const updateProductModelQuestion = (id, productModelQuestion) => updateItem('product-model-questions', id, productModelQuestion);
export const getProductModelQuestion = (id) => getItem('product-model-questions', id);
export const deleteProductModelQuestion = (id) => deleteItem('product-model-questions', id);
export const listProductModelQuestions = () => listItems('product-model-questions');
export const importProductModelQuestions = (file) => importData('product-model-questions', file);
export const exportProductModelQuestions = () => exportData('product-model-questions');

// ProductModelAnswer API
export const createProductModelAnswer = (productModelAnswer) => createItem('product-model-answers', productModelAnswer);
export const getProductModelAnswer = (id) => getItem('product-model-answers', id);
export const updateProductModelAnswer = (id, productModelAnswer) => updateItem('product-model-answers', id, productModelAnswer);
export const deleteProductModelAnswer = (id) => deleteItem('product-model-answers', id);
export const listProductModelAnswers = () => listItems('product-model-answers');
export const importProductModelAnswers = (file) => importData('product-model-answers', file);
export const exportProductModelAnswers = () => exportData('product-model-answers');

// MasterQuestion API
export const createMasterQuestion = (masterQuestion) => createItem('master-questions', masterQuestion);
export const getMasterQuestion = (id) => getItem('master-questions', id);
export const updateMasterQuestion = (id, masterQuestion) => updateItem('master-questions', id, masterQuestion);
export const deleteMasterQuestion = (id) => deleteItem('master-questions', id);
export const listMasterQuestions = () => listItems('master-questions');
export const importMasterQuestions = (file) => importData('master-questions', file);
export const exportMasterQuestions = () => exportData('master-questions');

// MasterAnswer API
export const createMasterAnswer = (masterAnswer) => createItem('master-answers', masterAnswer);
export const getMasterAnswer = (id) => getItem('master-answers', id);
export const updateMasterAnswer = (id, masterAnswer) => updateItem('master-answers', id, masterAnswer);
export const deleteMasterAnswer = (id) => deleteItem('master-answers', id);
export const listMasterAnswers = () => listItems('master-answers');
export const importMasterAnswers = (file) => importData('master-answers', file);
export const exportMasterAnswers = () => exportData('master-answers');

// StepOrder API
export const createStepOrder = (stepOrder) => createItem('step_orders', stepOrder);
export const getStepOrder = (id) => getItem('step_orders', id);
export const updateStepOrder = (id, stepOrder) => updateItem('step_orders', id, stepOrder);
export const deleteStepOrder = (id) => deleteItem('step_orders', id);
export const listStepOrders = () => listItems('step_orders');
export const importStepOrders = (file) => importData('step_orders', file);
export const exportStepOrders = async () => {
  try {
    const response = await axiosInstance.get(`step_orders/export_data/`, {
      responseType: 'blob'
    });
    const url = window.URL.createObjectURL(new Blob([response.data]));
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', `step_orders.xlsx`);
    document.body.appendChild(link);
    link.click();
    console.log(`Export successful for step_orders`);
  } catch (error) {
    console.error(`Error exporting data for step_orders:`, error);
    throw error;
  }
};

// Variant API
export const createVariant = (variant) => createItem('variants', variant);
export const getVariant = (id) => getItem('variants', id);
export const updateVariant = (id, variant) => updateItem('variants', id, variant);
export const deleteVariant = (id) => deleteItem('variants', id);
export const listVariants = () => listItems('variants');
export const importVariants = (file) => importData('variants', file);
export const exportVariants = () => exportData('variants');
