// path: frontend/src/components/formforgeapi/components/components/page-level/FormSchemaListScreen.jsx
import React, { useCallback, useEffect, useState } from 'react';
import { formforgeapiApi } from '../../../api/FormForgeApi';
import SchemaTable from '../reusable/SchemaTable';
import { toast } from 'react-toastify';

const FormSchemaListScreen = () => {
    const [schemas, setSchemas] = useState([]);
    const [loading, setLoading] = useState(true);

    const fetchSchemas = useCallback(async () => {
        setLoading(true);
        try {
            const response = await formforgeapiApi.getAllForms();
            setSchemas(response.data.data);
        } catch (error) {
            toast.error("Form şemaları alınırken bir hata oluştu.");
        } finally {
            setLoading(false);
        }
    }, []);

    useEffect(() => {
        fetchSchemas();
    }, [fetchSchemas]);

    const deleteSchema = useCallback(async (id) => {
        try {
            await formforgeapiApi.deleteForm(id);
            setSchemas(schemas.filter(schema => schema.id !== id));
            toast.success("Form şeması başarıyla silindi!");
        } catch (error) {
            toast.error("Form şeması silinirken bir hata oluştu.");
        }
    }, [schemas]);

    return (
        <div>
            <h2>Form Şemaları</h2>
            <SchemaTable schemas={schemas} loading={loading} deleteSchema={deleteSchema} />
        </div>
    );
};

export default FormSchemaListScreen;
