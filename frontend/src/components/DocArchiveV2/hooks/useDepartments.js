// frontend/src/components/DocArchiveV2/hooks/useDepartment.js
import { useState, useEffect } from 'react';
import { fetchDepartments, createDepartment, updateDepartment, deleteDepartment } from '../../../api/docarchivev2'; // API fonksiyonlarını import et

const useDepartments = () => {
    const [departments, setDepartments] = useState([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    const loadDepartments = async () => {
        setLoading(true);
        try {
            const results = await fetchDepartments();
            setDepartments(results); // API'den alınan 'results' dizisi doğrudan kullanılır
            setError(null);
        } catch (err) {
            setError("Departmanlar yüklenirken bir hata oluştu: " + err.message); // Hata mesajını ayarla
            setDepartments([]); // Hata durumunda departman listesini boş bir dizi olarak ayarla
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        loadDepartments();
    }, []);

    // Departman ekleme fonksiyonu
    const addDepartment = async (data) => {
        try {
            const newDepartment = await createDepartment(data);
            setDepartments([...departments, newDepartment]); // Yeni departmanı listeye ekle
        } catch (err) {
            setError("Departman eklenirken bir hata oluştu: " + err.message);
            throw err;
        }
    };

    // Departman güncelleme fonksiyonu
    const modifyDepartment = async (id, data) => {
        try {
            const updated = await updateDepartment(id, data);
            setDepartments(departments.map(dep => dep.id === id ? { ...dep, ...updated } : dep)); // Güncellenmiş departmanı listede güncelle
        } catch (err) {
            setError("Departman güncellenirken bir hata oluştu: " + err.message);
            throw err;
        }
    };

    // Departman silme fonksiyonu
    const removeDepartment = async (id) => {
        try {
            await deleteDepartment(id);
            setDepartments(departments.filter(dep => dep.id !== id)); // Silinen departmanı listeden çıkar
        } catch (err) {
            setError("Departman silinirken bir hata oluştu: " + err.message);
            throw err;
        }
    };

    return {
        departments,
        loading,
        error,
        addDepartment,
        modifyDepartment,
        removeDepartment
    };
};

export default useDepartments;

