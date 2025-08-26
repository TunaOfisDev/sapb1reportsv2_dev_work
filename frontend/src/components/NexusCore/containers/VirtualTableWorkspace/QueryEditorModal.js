// path: frontend/src/components/NexusCore/containers/VirtualTableWorkspace/QueryEditorModal.jsx
import React, { useState, useEffect } from 'react';
import PropTypes from 'prop-types';
import styles from './QueryEditorModal.module.scss';

// Gerçek, ortak bileşenlerimizi import ediyoruz
import Modal from '../../components/common/Modal/Modal';
import Input from '../../components/common/Input/Input';
import Select from '../../components/common/Select/Select';
import Textarea from '../../components/common/Textarea/Textarea';
import Button from '../../components/common/Button/Button';

const SHARING_OPTIONS = [
    { value: 'PRIVATE', label: 'Özel (Sadece Ben)' },
    { value: 'PUBLIC_READONLY', label: 'Halka Açık (Salt Okunur)' },
];

const QueryEditorModal = ({ isOpen, onClose, onSubmit, initialData = null, connections = [], isSaving = false }) => {
    const [title, setTitle] = useState('');
    const [sqlQuery, setSqlQuery] = useState('');
    const [connectionId, setConnectionId] = useState('');
    const [sharingStatus, setSharingStatus] = useState('PRIVATE');
    
    const isEditMode = initialData !== null;

    useEffect(() => {
        if (isOpen) {
            if (isEditMode) {
                setTitle(initialData.title || '');
                setSqlQuery(initialData.sql_query || '');
                setConnectionId(initialData.connection || '');
                setSharingStatus(initialData.sharing_status || 'PRIVATE');
            } else {
                setTitle('');
                setSqlQuery('SELECT * \nFROM \nWHERE ');
                setConnectionId(connections.length > 0 ? connections[0].id : '');
                setSharingStatus('PRIVATE');
            }
        }
    }, [isOpen, initialData, isEditMode, connections]);

    const handleSubmit = (e) => {
        e.preventDefault();
        const formData = {
            title,
            sql_query: sqlQuery,
            connection_id: connectionId,
            sharing_status: sharingStatus
        };
        onSubmit(formData);
    };

    const connectionOptions = connections.map(c => ({ value: c.id, label: c.title }));

    return (
        <Modal 
            isOpen={isOpen} 
            onClose={onClose} 
            title={isEditMode ? `Düzenle: ${initialData?.title}` : 'Yeni Sorgu Oluştur'}
        >
            <form onSubmit={handleSubmit}>
                {/* ### YENİ: Form elemanları artık CSS Grid ile hizalanıyor ### */}
                <div className={styles.formGrid}>
                    <Input
                        id="vt-title"
                        label="Sorgu Başlığı"
                        value={title}
                        onChange={(e) => setTitle(e.target.value)}
                        required
                    />
                    <Select
                        id="vt-connection"
                        label="Veri Kaynağı"
                        value={connectionId}
                        onChange={(e) => setConnectionId(e.target.value)}
                        options={connectionOptions}
                        required
                        disabled={isEditMode}
                    />
                    <div className={styles.fullWidth}>
                        <Textarea
                            id="vt-sql"
                            label="SQL Sorgusu"
                            value={sqlQuery}
                            onChange={(e) => setSqlQuery(e.target.value)}
                            rows={10}
                            required
                            style={{ fontFamily: 'monospace' }}
                        />
                    </div>
                    <Select
                        id="vt-sharing"
                        label="Paylaşım Durumu"
                        value={sharingStatus}
                        onChange={(e) => setSharingStatus(e.target.value)}
                        options={SHARING_OPTIONS}
                        required
                    />
                </div>
                
                <div className={styles.actions}>
                    <Button type="button" variant="secondary" onClick={onClose} disabled={isSaving}>
                        Vazgeç
                    </Button>
                    <Button type="submit" variant="primary" disabled={isSaving || !title || !connectionId || !sqlQuery}>
                        {isSaving ? 'Kaydediliyor...' : (isEditMode ? 'Güncelle' : 'Oluştur')}
                    </Button>
                </div>
            </form>
        </Modal>
    );
};

QueryEditorModal.propTypes = {
    isOpen: PropTypes.bool.isRequired,
    onClose: PropTypes.func.isRequired,
    onSubmit: PropTypes.func.isRequired,
    initialData: PropTypes.object,
    connections: PropTypes.array,
    isSaving: PropTypes.bool,
};

export default QueryEditorModal;