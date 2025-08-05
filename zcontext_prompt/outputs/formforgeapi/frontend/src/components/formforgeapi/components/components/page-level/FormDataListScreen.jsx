// path: frontend/src/components/formforgeapi/components/components/page-level/FormDataListScreen.jsx
import React, { useMemo, useEffect, useState, useCallback } from 'react';
import { useParams } from 'react-router-dom';
import { formforgeapiApi } from '../../../api/FormForgeApi';
import DataTable from '../reusable/DataTable';
import styles from '../../../css/FormForgeAPI.module.css';
import { toast } from 'react-toastify';

const FormDataListScreen = () => {
    const { formId } = useParams();
    const [submissions, setSubmissions] = useState([]);
    const [columns, setColumns] = useState([]);
    const [loading, setLoading] = useState(true);
    const [formFields, setFormFields] = useState([]);

    const fetchFormData = useCallback(async () => {
        setLoading(true);
        try {
            const submissionsResponse = await formforgeapiApi.getFormSubmissions(formId);
            if (submissionsResponse && submissionsResponse.data && submissionsResponse.data.data) {
                setSubmissions(submissionsResponse.data.data);
            }

            const fieldsResponse = await formforgeapiApi.getFormFields(formId);
            if (fieldsResponse && fieldsResponse.data) {
                setFormFields(fieldsResponse.data);
                const masterColumns = fieldsResponse.data.filter(field => field.is_master).map(field => ({
                    Header: field.label,
                    accessor: `values.${field.id}.value` // Accessing nested data
                }));
                setColumns(masterColumns);
            }
        } catch (error) {
            toast.error("Veriler alınırken bir hata oluştu.");
            console.error("Error fetching form data:", error);
        } finally {
            setLoading(false);
        }
    }, [formId]);

    useEffect(() => {
        fetchFormData();
    }, [fetchFormData]);


    const data = useMemo(() => submissions, [submissions]);

    return (
        <div>
            <h2>Form Verileri</h2>
            <DataTable columns={columns} data={data} loading={loading} />
        </div>
    );
};

export default FormDataListScreen;
