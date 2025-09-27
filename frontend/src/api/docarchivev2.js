// frontend/src/api/docarchivev2.js
import axios from './axiosconfig';

const apiUrl = '/docarchivev2/';

// Department API Operations
export const fetchDepartments = async () => {
    try {
        const response = await axios.get(`${apiUrl}departments/`);
        return response.data.results; // API'den gelen 'results' dizisini döndür
    } catch (error) {
        console.error("Error fetching departments: ", error.response ? error.response.data : error.message);
        throw error;
    }
};

export const createDepartment = (data) => axios.post(`${apiUrl}departments/`, data);
export const updateDepartment = (id, data) => axios.put(`${apiUrl}departments/${id}/`, data);
export const deleteDepartment = (id) => axios.delete(`${apiUrl}departments/${id}/`);

// Document API Operations
export const fetchDocuments = async () => {
    try {
        const response = await axios.get(`${apiUrl}documents/`);
        return response.data.results; // API'den gelen 'results' dizisini döndür
    } catch (error) {
        console.error("Error fetching documents: ", error.response ? error.response.data : error.message);
        throw error;
    }
};

export const fetchDocumentById = (id) => axios.get(`${apiUrl}documents/${id}/`);
export const createDocument = (data) => {
    return axios.post(`${apiUrl}documents/`, data, {
        headers: {
            'Content-Type': 'multipart/form-data'
        }
    }).then(response => {
        console.log("Document created successfully: ", response.data);
        return response.data;
    }).catch(error => {
        console.error("Error creating document: ", error.response ? error.response.data : error.message);
        throw error;
    });
};

export const updateDocument = (id, data) => axios.put(`${apiUrl}documents/${id}/`, data);
export const deleteDocument = (id) => axios.delete(`${apiUrl}documents/${id}/`);


