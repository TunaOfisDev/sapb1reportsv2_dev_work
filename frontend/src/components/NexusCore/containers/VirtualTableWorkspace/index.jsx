// path: frontend/src/components/NexusCore/containers/VirtualTableWorkspace/index.jsx
import React, { useState, useEffect, useCallback } from 'react';
// ### YENİ: Navigasyon için Link bileşenini import ediyoruz ###
import { Link } from 'react-router-dom';
// ### YENİ: Playground butonu için bir ikon seçelim ###
import { PlusCircle, Sliders } from 'react-feather';
import styles from './VirtualTableWorkspace.module.scss';

// Hook'lar ve API'ler
import { useApi } from '../../hooks/useApi';
import { useNotifications } from '../../hooks/useNotifications';
import * as virtualTablesApi from '../../api/virtualTablesApi';
import * as connectionsApi from '../../api/connectionsApi';

// Bileşenler
import Card from '../../components/common/Card/Card';
import Button from '../../components/common/Button/Button';
import Spinner from '../../components/common/Spinner/Spinner';
import Table from '../../components/common/Table/Table';
import VirtualTableList from './VirtualTableList';
import QueryEditorModal from './QueryEditorModal';

const VirtualTableWorkspace = () => {
    // ... (dosyanın başındaki tüm state ve fonksiyon tanımları aynı kalıyor) ...
    const { data: tablesResponse, error: listError, loading: listLoading, request: fetchTables } = useApi(virtualTablesApi.getVirtualTables);
    const { data: connectionsResponse, request: fetchConnections } = useApi(connectionsApi.getConnections);
    const { data: tableData, error: executeError, loading: executeLoading, request: executeQuery } = useApi(virtualTablesApi.executeVirtualTable);
    const createApi = useApi(virtualTablesApi.createVirtualTable);
    const updateApi = useApi(virtualTablesApi.updateVirtualTable);
    const deleteApi = useApi(virtualTablesApi.deleteVirtualTable);

    const [isModalOpen, setIsModalOpen] = useState(false);
    const [editingTable, setEditingTable] = useState(null);
    const [selectedTable, setSelectedTable] = useState(null);
    const { addNotification } = useNotifications();

    const memoizedFetchTables = useCallback(fetchTables, []);
    const memoizedFetchConnections = useCallback(fetchConnections, []);

    useEffect(() => {
        memoizedFetchTables();
        memoizedFetchConnections();
    }, [memoizedFetchTables, memoizedFetchConnections]);

    const handleExecute = (table) => {
        setSelectedTable(table);
        executeQuery(table.id);
    };

    const handleDelete = async (table) => {
        if (window.confirm(`'${table.title}' başlıklı sorguyu silmek istediğinizden emin misiniz?`)) {
            const { success } = await deleteApi.request(table.id);
            if(success) {
                addNotification("Sorgu başarıyla silindi.", "success");
                fetchTables();
                if(selectedTable && selectedTable.id === table.id) {
                    setSelectedTable(null);
                }
            } else {
                addNotification("Sorgu silinirken bir hata oluştu.", "error");
            }
        }
    };
    
    const handleFormSubmit = async (formData) => {
        const isEditMode = !!editingTable;
        let result;
        if (isEditMode) {
            result = await updateApi.request(editingTable.id, formData);
        } else {
            result = await createApi.request(formData);
        }

        if(result.success) {
            addNotification(isEditMode ? 'Sorgu başarıyla güncellendi.' : 'Sorgu başarıyla oluşturuldu.', 'success');
            setIsModalOpen(false);
            fetchTables();
        } else {
            const errorMessage = result.error?.response?.data?.sql_query?.[0] || 'İşlem sırasında bir hata oluştu.';
            addNotification(errorMessage, 'error');
        }
    };

    const tables = tablesResponse?.results || [];
    const connections = connectionsResponse?.results || [];
    
    return (
        <div className={styles.workspaceContainer}>
            <Card
                title="Sanal Tablolarım"
                headerActions={
                    <Button onClick={() => { setEditingTable(null); setIsModalOpen(true); }} IconComponent={PlusCircle}>
                        Yeni Sorgu Oluştur
                    </Button>
                }
            >
                {listLoading ? <Spinner /> : 
                    <VirtualTableList 
                        tables={tables} 
                        onExecute={handleExecute} 
                        onEdit={(table) => { setEditingTable(table); setIsModalOpen(true); }} 
                        onDelete={handleDelete} 
                    />
                }
                 {listError && <p style={{color: 'red', textAlign: 'center', marginTop: '20px'}}>Sorgu listesi yüklenirken bir hata oluştu.</p>}
            </Card>

            {selectedTable && (
                <Card 
                    title={`Sonuçlar: ${selectedTable.title}`} 
                    className={styles.resultsCard}
                    // ### YENİ: Sonuçlar kartına "Oyun Alanı" butonu ekliyoruz ###
                    headerActions={
                        <Link to={`/nexus/playground/${selectedTable.id}`}>
                            <Button variant="primary" IconComponent={Sliders}>
                                Oyun Alanına Git
                            </Button>
                        </Link>
                    }
                >
                    <Table 
                        data={tableData}
                        loading={executeLoading}
                        error={executeError}
                    />
                </Card>
            )}

            <QueryEditorModal 
                isOpen={isModalOpen}
                onClose={() => setIsModalOpen(false)}
                onSubmit={handleFormSubmit}
                initialData={editingTable}
                connections={connections}
                isSaving={createApi.loading || updateApi.loading}
            />
        </div>
    );
};

export default VirtualTableWorkspace;