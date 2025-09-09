// path: frontend/src/components/NexusCore/containers/AdminPanel/DBTypeMappings.jsx

import React, { useEffect } from 'react';
import { useDbTypeMappings } from '../../hooks/useDbTypeMappings';
import Spinner from '../../components/common/Spinner/Spinner';
import Table from '../../components/common/Table/Table';

const DBTypeMappings = () => {
    // Hook'u kullanarak veri ve durumları alıyoruz
    const { mappings, isLoading, error, loadMappings, updateMapping, deleteMapping } = useDbTypeMappings();

    useEffect(() => {
        // Bileşen yüklendiğinde eşleştirmeleri çek
        loadMappings();
    }, [loadMappings]);

    if (isLoading) {
        return <Spinner />;
    }

    if (error) {
        return <p>Veri tipi eşleştirmeleri yüklenirken bir hata oluştu.</p>;
    }

    const handleUpdate = (id, newCategory) => {
        updateMapping(id, { general_category: newCategory });
    };

    const handleDelete = (id) => {
        deleteMapping(id);
    };

    // Tablo verisini formatlamadan Table bileşenine veriyoruz.
    // Table bileşeninin içindeki mantık, formatlamayı kendisi yapar.
    const columns = [
        { Header: 'DB Tipi', accessor: 'db_type' },
        { Header: 'Orijinal Tip', accessor: 'source_type' },
        { Header: 'Genel Kategori', accessor: 'general_category' },
        { Header: 'Eylemler', accessor: 'actions' },
    ];

    const data = mappings.map(mapping => ({
        ...mapping,
        actions: (
            <>
                <button onClick={() => handleUpdate(mapping.id, 'number')}>Sayıya Çevir</button>
                <button onClick={() => handleUpdate(mapping.id, 'string')}>Metne Çevir</button>
                <button onClick={() => handleDelete(mapping.id)}>Sil</button>
            </>
        )
    }));

    return (
        <div>
            <h2>Veri Tipi Eşleştirmeleri</h2>
            <Table columns={columns} data={data} />
        </div>
    );
};

export default DBTypeMappings;