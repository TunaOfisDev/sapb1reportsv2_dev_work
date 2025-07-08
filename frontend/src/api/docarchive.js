// frontend/src/api/docarchive.js
import axios from './axiosconfig';

export const BASE_URL = '/docarchive/documents';
export const DEPARTMENT_URL = '/docarchive/departments';
export const DOCUMENT_FILE_URL = '/docarchive/document-files';

// Existing Document endpoints
export const fetchDocuments = () => axios.get(`${BASE_URL}/`);
export const fetchDocumentById = (id) => axios.get(`${BASE_URL}/${id}/`);
export const createDocument = (documentData) => axios.post(`${BASE_URL}/`, documentData);
export const updateDocument = (id, documentData) => axios.put(`${BASE_URL}/${id}/`, documentData);
export const deleteDocument = (id) => axios.delete(`${BASE_URL}/${id}/`);

// Existing Department endpoints
export const fetchDepartments = () => axios.get(`${DEPARTMENT_URL}/`);
export const fetchDepartmentById = (id) => axios.get(`${DEPARTMENT_URL}/${id}/`);
export const createDepartment = (departmentData) => axios.post(`${DEPARTMENT_URL}/`, departmentData);
export const updateDepartment = (id, departmentData) => axios.put(`${DEPARTMENT_URL}/${id}/`, departmentData);
export const deleteDepartment = (id) => axios.delete(`${DEPARTMENT_URL}/${id}/`);

// New DocumentFile endpoints
export const fetchDocumentFiles = () => axios.get(`${DOCUMENT_FILE_URL}/`);
export const fetchFilesForDocument = (documentId) => axios.get(`${BASE_URL}/${documentId}/files/`);
export const createDocumentFile = (documentFileData) => axios.post(`${DOCUMENT_FILE_URL}/`, documentFileData);
export const updateDocumentFile = (id, documentFileData) => axios.put(`${DOCUMENT_FILE_URL}/${id}/`, documentFileData);
export const deleteDocumentFile = (id) => axios.delete(`${DOCUMENT_FILE_URL}/${id}/`);  // Ensure this is correctly exported

