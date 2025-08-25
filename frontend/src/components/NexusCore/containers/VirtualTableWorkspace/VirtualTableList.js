/* path: frontend/src/components/NexusCore/containers/VirtualTableWorkspace/VirtualTableList.js */

import React, { useState, useEffect } from 'react';
import styles from './VirtualTableList.module.scss';

// Hook'larımızı ve API modüllerimizi import ediyoruz
import { useApi } from '../../hooks/useApi';
import { useNotifications } from '../../hooks/useNotifications';
import * as virtualTablesApi from '../../api/virtualTablesApi';
import * as connectionsApi from '../../api/connectionsApi';
import { formatSharingStatus } from '../../utils/formatters';

// Diğer bileşenlerimizi import ediyoruz
import QueryEditorModal from './QueryEditorModal';
import DataTable from './DataTable';

// Common bileşenlerimizin burada olduğunu varsayıyoruz
/* import { Button } from '../../components/common/Button/Button'; */
/* import { Spinner } from '../../components/common/Spinner/Spinner'; */
const Button = ({ children, onClick, variant, IconComponent }) => <button onClick={onClick}>{IconComponent && <IconComponent />}{children}</button>;
const Spinner = () => <div>Yükleniyor...</div>;

// İkonları import ettiğimizi varsayalım
const PlusCircleIcon = () => <span>+</span>; 
const PlayIcon = () => <span>▶</span>;
const EditIcon = () => <span>✎</span>;
const TrashIcon = () => <span>🗑</span>;


const VirtualTableList = () => {
    // --- State Yönetimi ---
    // API'ler için birden fazla useApi hook'u kullanıyoruz. Her biri kendi state'ini yönetir.
    const { data: tables, error: listError, loading: listLoading, request: fetchTables } = useApi(virtualTablesApi.getVirtualTables);
    const { data: connections, request: fetchConnections } = useApi(connectionsApi.getConnections);
    const { data: tableData, error: executeError, loading: executeLoading, request: executeQuery } = useApi(virtualTablesApi.executeVirtualTable);
    const createApi = useApi(virtualTablesApi.createVirtualTable);
    const updateApi = useApi(virtualTablesApi.updateVirtualTable);
    const deleteApi = useApi(virtualTablesApi.deleteVirtualTable);

    // Modal'ın durumunu yönetmek için
    const [isModalOpen, setIsModalOpen] = useState(false);
    const [editingTable, setEditingTable] = useState(null); // Düzenlenen tabloyu tutar
    
    // Hangi tablonun verisinin gösterildiğini tutmak için
    const [selectedTable, setSelectedTable] = useState(null);

    const { addNotification } = useNotifications();

    // --- Veri Çekme ---
    useEffect(() => {
        fetchTables();
        fetchConnections();
    }, []); // Boş dependency array, sadece ilk render'da çalışmasını sağlar.

    // --- Olay Yöneticileri (Event Handlers) ---
    const handleOpenCreateModal = () => {
        setEditingTable(null);
        setIsModalOpen(true);
    };

    const handleOpenEditModal = (table) => {
        setEditingTable(table);
        setIsModalOpen(true);
    };

    const handleExecute = (table) => {
        setSelectedTable(table);
        executeQuery(table.id);
    };

    const handleDelete = async (table) => {
        if (window.confirm(`'${table.title}' başlıklı sorguyu silmek istediğinizden emin misiniz?`)) {
            const { success } = await deleteApi.request(table.id);
            if(success) {
                addNotification("Sorgu başarıyla silindi.", "success");
                fetchTables(); // Listeyi yenile
            } else {
                addNotification("Sorgu silinirken bir hata oluştu.", "error");
            }
        }
    };

    const handleFormSubmit = async (formData) => {
        const isEditMode = !!editingTable;
        const apiToCall = isEditMode ? updateApi : createApi;
        const id = isEditMode ? editingTable.id : null;
        
        const { success } = await apiToCall.request(id, formData);

        if(success) {
            addNotification(isEditMode ? 'Sorgu başarıyla güncellendi.' : 'Sorgu başarıyla oluşturuldu.', 'success');
            setIsModalOpen(false);
            fetchTables(); // Listeyi yenile
        } else {
            addNotification('İşlem sırasında bir hata oluştu.', 'error');
        }
    };

    // --- Arayüz Çizimi ---
    if (listLoading) return <Spinner />;
    if (listError) return <div>Hata: Sanal tablolar yüklenemedi.</div>;

    return (
        <div className={styles.workspace}>
            <div className={styles.header}>
                <h1 className={styles.header__title}>Sanal Tablolar (Oyun Alanı)</h1>
                <Button variant="primary" IconComponent={PlusCircleIcon} onClick={handleOpenCreateModal}>
                    Yeni Sorgu Oluştur
                </Button>
            </div>

            <ul className={styles.tableList}>
                {tables?.map(table => {
                    const status = formatSharingStatus(table.sharing_status);
                    return (
                        <li key={table.id} className={styles.tableListItem}>
                            <div className={styles.tableListItem__info}>
                                <h3 className={styles.tableListItem__title}>{table.title}</h3>
                                <span className={styles.tableListItem__status}>
                                    {/* <StatusIcon iconName={status.icon} /> */}
                                    {status.text}
                                </span>
                            </div>
                            <div className={styles.tableListItem__actions}>
                                <Button variant="secondary" IconComponent={PlayIcon} onClick={() => handleExecute(table)}>
                                    Çalıştır
                                </Button>
                                <Button variant="secondary" IconComponent={EditIcon} onClick={() => handleOpenEditModal(table)}>
                                    Düzenle
                                </Button>
                                <Button variant="danger" IconComponent={TrashIcon} onClick={() => handleDelete(table)}>
                                    Sil
                                </Button>
                            </div>
                        </li>
                    )
                })}
            </ul>
            
            {selectedTable && (
                <div className={styles.dataView}>
                    <h2 className={styles.dataView__header}>
                        Sonuçlar: <strong>{selectedTable.title}</strong>
                    </h2>
                    <DataTable 
                        data={tableData}
                        loading={executeLoading}
                        error={executeError}
                        columnMetadata={selectedTable.column_metadata}
                    />
                </div>
            )}

            <QueryEditorModal 
                isOpen={isModalOpen}
                onClose={() => setIsModalOpen(false)}
                onSubmit={handleFormSubmit}
                initialData={editingTable}
                connections={connections || []}
                loading={createApi.loading || updateApi.loading}
            />
        </div>
    );
};

export default VirtualTableList;