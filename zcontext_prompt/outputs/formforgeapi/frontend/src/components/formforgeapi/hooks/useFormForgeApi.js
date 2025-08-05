// path: frontend/src/components/formforgeapi/hooks/useFormForgeApi.js
import { useState, useCallback } from 'react';
import { toast } from 'react-toastify';
import { formforgeapiApi } from '../api/FormForgeApi';

export const useFormForgeApi = () => {
    const [departments, setDepartments] = useState([]);
    const [loadingDepartments, setLoadingDepartments] = useState(false);
    const [forms, setForms] = useState([]);
    const [loadingForms, setLoadingForms] = useState(false);

    const fetchDepartments = useCallback(async (params) => {
        setLoadingDepartments(true);
        try {
            const response = await formforgeapiApi.getAllDepartments(params);
            setDepartments(response.data.data || []);
        } catch (error) {
            toast.error("Departmanlar alınırken bir hata oluştu.");
        } finally {
            setLoadingDepartments(false);
        }
    }, []);

    const fetchForms = useCallback(async (params) => {
        setLoadingForms(true);
        try {
            const response = await formforgeapiApi.getAllForms(params);
            setForms(response.data.data || []);
        } catch (error) {
            toast.error("Formlar alınırken bir hata oluştu.");
        } finally {
            setLoadingForms(false);
        }
    }, []);


    return {
        departments,
        loadingDepartments,
        fetchDepartments,
        forms,
        loadingForms,
        fetchForms
    };
};
