// frontend/src/components/DocArchiveV2/views/DocumentForm.js
import React, { useState, useEffect } from 'react';
import { toast } from 'react-toastify';
import useDocuments from '../hooks/useDocuments';
import useDepartments from '../hooks/useDepartments';
import '../css/DocumentForm.css';

const DocumentForm = ({ documentId, reloadDocuments }) => {
    const { createDocument, updateDocument, fetchDocumentById } = useDocuments();
    const { departments, loading: loadingDepts, error: errorDepts } = useDepartments();
    const [formData, setFormData] = useState({
        name: '',
        owner_name: '',
        comments: '',
        departmentId: '',
        files: []
    });
    const [isVisible, setIsVisible] = useState(false);  // Formun görünürlüğünü kontrol eden state

    useEffect(() => {
        if (documentId) {
            fetchDocumentById(documentId).then(data => {
                setFormData({
                    name: data.name,
                    owner_name: data.owner_name,
                    comments: data.comments,
                    departmentId: data.department ? data.department.id : '',
                    files: []
                });
            });
        }
    }, [documentId, fetchDocumentById]);

    const handleInputChange = (event) => {
        const { name, value } = event.target;
        setFormData(prev => ({ ...prev, [name]: value }));
    };

    const handleFileChange = (event) => {
        setFormData(prev => ({ ...prev, files: Array.from(event.target.files) }));
    };

    const resetForm = () => {
        setFormData({
            name: '',
            owner_name: '',
            comments: '',
            departmentId: '',
            files: []
        });
    };

    const handleSubmit = async (event) => {
        event.preventDefault();
        const data = new FormData();
        data.append('name', formData.name);
        data.append('owner_name', formData.owner_name);
        data.append('comments', formData.comments);
        data.append('department', formData.departmentId);
        formData.files.forEach(file => {
            data.append('file', file);
        });

        try {
            if (documentId) {
                await updateDocument(documentId, data);
                toast.success("Belge başarıyla güncellendi!");
            } else {
                await createDocument(data);
                toast.success("Belge başarıyla oluşturuldu!");
            }
            resetForm();  // Formu temizle
            reloadDocuments();  // Belge listesini yeniden yükle
        } catch (error) {
            toast.error("Belge kaydedilirken hata oluştu: " + error.message);
        }
    };

    if (loadingDepts) {
        return <p>Departmanlar yükleniyor...</p>;
    }

    if (errorDepts) {
        return <p>Departmanları yüklerken hata oluştu: {errorDepts.message}</p>;
    }

    return (
        <>
            <button onClick={() => setIsVisible(!isVisible)} className="DocumentForm__button">
                {isVisible ? 'Formu Gizle' : 'Yeni Belge Ekle'}
            </button>
            {isVisible && (
                <form className="DocumentForm__form" onSubmit={handleSubmit}>
            <div className="DocumentForm__form-group">
                <label className="DocumentForm__label">Ad:</label>
                <input
                    className="DocumentForm__input"
                    type="text"
                    name="name"
                    value={formData.name}
                    onChange={handleInputChange}
                    required
                />
            </div>
            <div className="DocumentForm__form-group">
                <label className="DocumentForm__label">Sahibi:</label>
                <input
                    className="DocumentForm__input"
                    type="text"
                    name="owner_name"
                    value={formData.owner_name}
                    onChange={handleInputChange}
                    required
                />
            </div>
            <div className="DocumentForm__form-group">
                <label className="DocumentForm__label">Yorumlar:</label>
                <textarea
                    className="DocumentForm__textarea"
                    name="comments"
                    value={formData.comments}
                    onChange={handleInputChange}
                ></textarea>
            </div>
            <div className="DocumentForm__form-group">
            <label className="DocumentForm__label">Department:</label>
                <select
                    className="DocumentForm__input"
                    name="departmentId"
                    value={formData.departmentId}
                    onChange={handleInputChange}
                    required
                >
                    <option value="">Select a Department</option>
                    {departments && departments.map(dept => (
                        <option key={dept.id} value={dept.id}>{dept.name}</option>
                    ))}
                </select>
            </div>
            <div className="DocumentForm__form-group">
                <label className="DocumentForm__label">Dosyalar:</label>
                <input
                    type="file"
                    multiple
                    onChange={handleFileChange}
                />
            </div>
            <button type="submit" className="DocumentForm__button">Belge Kaydet</button>
            </form>
            )}
        </>
    );
};

export default DocumentForm;
