// path: frontend/src/components/formforgeapi/components/components/page-level/FormFillScreen.jsx
import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import { useForm } from "react-hook-form";
import { formforgeapiApi } from '../../../api/FormForgeApi';
import { toast } from 'react-toastify';

const FormFillScreen = () => {
    const { formId } = useParams();
    const { register, handleSubmit, reset, formState: { errors } } = useForm();
    const [fields, setFields] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchFields = async () => {
            setLoading(true);
            try {
                const response = await formforgeapiApi.getFormFields(formId);
                setFields(response.data);
            } catch (error) {
                toast.error("Form alanları alınırken bir hata oluştu.");
            } finally {
                setLoading(false);
            }
        };

        fetchFields();
    }, [formId]);

    const onSubmit = async (data) => {
        try {
            const response = await formforgeapiApi.createFormSubmission({ form: formId, submitted_data: data });
            toast.success("Form başarıyla gönderildi!");
            reset(); // Formu temizle
        } catch (error) {
            toast.error("Form gönderilirken bir hata oluştu.");
        }
    };

    if (loading) {
        return <div>Yükleniyor...</div>;
    }

    return (
        <form onSubmit={handleSubmit(onSubmit)}>
            {fields.map(field => (
                <div key={field.id}>
                    <label htmlFor={field.id}>{field.label}</label>
                    <input type={field.field_type} {...register(String(field.id), { required: field.is_required })} />
                    {errors[field.id] && <p>{field.label} alanı zorunludur.</p>}
                </div>
            ))}
            <input type="submit" value="Gönder" />
        </form>
    );
};

export default FormFillScreen;
