// frontend/src/components/NewCustomerForm/containers/EditCustomerForm.js
import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { retrieveUserNewCustomerForm, updateUserNewCustomerForm } from '../../../api/newcustomerform';
import NewCustomerForm from '../forms/NewCustomerForm';
import customerFormToasts from '../utils/toast';

const EditCustomerForm = () => {
  const { id } = useParams(); // URL'den form ID'sini al
  const navigate = useNavigate();
  const [formData, setFormData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchFormData = async () => {
      try {
        const data = await retrieveUserNewCustomerForm(id);
        setFormData(data);
      } catch (error) {
        console.error('Form verisi alınırken hata:', error);
        customerFormToasts.error('Form verisi alınamadı');
        navigate('/newcustomerform');
      } finally {
        setLoading(false);
      }
    };

    fetchFormData();
  }, [id, navigate]);

  const handleSubmit = async (updatedData) => {
    try {
      await updateUserNewCustomerForm(id, updatedData);
      customerFormToasts.success('Form başarıyla güncellendi');
      navigate('/newcustomerform');
    } catch (error) {
      console.error('Form güncellenirken hata:', error);
      customerFormToasts.error('Form güncellenemedi');
    }
  };

  if (loading) {
    return <div>Yükleniyor...</div>;
  }

  return (
    <div className="edit-customer-form">
      <div className="edit-customer-form__header">
        <h2>Müşteri Formu Düzenle</h2>
        <p>Form ID: {id}</p>
      </div>

      <NewCustomerForm 
        initialData={formData}
        onSubmit={handleSubmit}
        isEdit={true}
      />
    </div>
  );
};

export default EditCustomerForm;