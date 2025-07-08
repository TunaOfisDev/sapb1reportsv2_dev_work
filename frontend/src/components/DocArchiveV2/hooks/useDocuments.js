// frontend/src/components/DocArchiveV2/hooks/useDocument.js
import { useState, useEffect, useMemo, useCallback } from 'react';
import axios from '../../../api/axiosconfig';
import useDepartments from './useDepartments';

const useDocuments = () => {
    const [documents, setDocuments] = useState([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const { departments, loading: deptsLoading, error: deptsError } = useDepartments();

    const departmentsMap = useMemo(() => {
        return departments.reduce((acc, dept) => {
            acc[dept.id] = dept.name;
            return acc;
        }, {});
    }, [departments]);

    const fetchDocuments = useCallback(async () => {
        setLoading(true);
        try {
            const response = await axios.get('/docarchivev2/documents/');
            const docs = response.data.results.map(doc => ({
                ...doc,
                departmentName: departmentsMap[doc.department] || 'No Department'
            }));
            setDocuments(docs);
            setError(null);
        } catch (err) {
            setError(err.message);
            setDocuments([]);
        } finally {
            setLoading(false);
        }
    }, [departmentsMap]);

    useEffect(() => {
        if (!deptsLoading && !deptsError) {
            fetchDocuments();
        }
    }, [deptsLoading, deptsError, fetchDocuments]);

    const fetchDocumentById = async (id) => {
        setLoading(true);
        try {
            const response = await axios.get(`/docarchivev2/documents/${id}/`);
            setLoading(false);
            return {
                ...response.data,
                departmentName: departmentsMap[response.data.department] || 'No Department'
            };
        } catch (err) {
            setError(err);
            setLoading(false);
            throw err;
        }
    };

    const createDocument = async (data) => {
        try {
            const response = await axios.post('/docarchivev2/documents/', data, {
                headers: {
                    'Content-Type': 'multipart/form-data'
                }
            });
            const newDoc = {
                ...response.data,
                departmentName: departmentsMap[response.data.department] || 'No Department'
            };
            setDocuments(prevDocs => [...prevDocs, newDoc]);
            return newDoc;
        } catch (err) {
            throw err;
        }
    };

    const updateDocument = async (id, data) => {
        try {
            const response = await axios.put(`/docarchivev2/documents/${id}/`, data);
            const updatedDoc = {
                ...response.data,
                departmentName: departmentsMap[response.data.department] || 'No Department'
            };
            setDocuments(prevDocs => prevDocs.map(doc => 
                doc.id === id ? updatedDoc : doc
            ));
            return updatedDoc;
        } catch (err) {
            throw err;
        }
    };

    const deleteDocument = async (id) => {
        try {
            await axios.delete(`/docarchivev2/documents/${id}/`);
            setDocuments(prevDocs => prevDocs.filter(doc => doc.id !== id));
        } catch (err) {
            throw err;
        }
    };

    return {
        documents,
        loading: loading || deptsLoading,
        error: error || deptsError,
        fetchDocumentById,
        fetchDocuments,
        createDocument,
        updateDocument,
        deleteDocument
    };
};

export default useDocuments;



