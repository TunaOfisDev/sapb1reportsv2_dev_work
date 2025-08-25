/* path: frontend/src/components/NexusCore/containers/VirtualTableWorkspace/QueryEditorModal.js */

import React, { useState, useEffect } from 'react';
import styles from './QueryEditorModal.module.scss';

/* Bu bileşenlerin `components/common/` altında oluşturulduğunu varsayıyoruz. */
/* import { Modal } from '../../components/common/Modal/Modal'; */
/* import { Input } from '../../components/common/Input/Input'; */
/* import { Select } from '../../components/common/Select/Select'; */
/* import { Button } from '../../components/common/Button/Button'; */

// Gerçek bileşenler hazır olana kadar geçici (placeholder) bileşenler kullanalım.
const Modal = ({ isOpen, onClose, title, children }) => isOpen ? <div className="modal-placeholder">{title}{children}<button onClick={onClose}>Close</button></div> : null;
const Input = ({ label, value, onChange }) => <div><label>{label}</label><input value={value} onChange={onChange} /></div>;
const Select = ({ label, value, onChange, children }) => <div><label>{label}</label><select value={value} onChange={onChange}>{children}</select></div>;
const Button = ({ children, onClick, variant, disabled }) => <button onClick={onClick} disabled={disabled}>{children}</button>;


const SHARING_OPTIONS = [
    { value: 'PRIVATE', label: 'Özel (Sadece Ben)' },
    { value: 'PUBLIC_READONLY', label: 'Halka Açık (Salt Okunur)' },
    { value: 'PUBLIC_EDITABLE', label: 'Halka Açık (Düzenlenebilir)' },
];

/**
 * Yeni Sanal Tablo oluşturmak veya mevcut olanı düzenlemek için kullanılan modal.
 * @param {object} props
 * @param {boolean} props.isOpen - Modal'ın açık olup olmadığını belirtir.
 * @param {Function} props.onClose - Modal'ı kapatma fonksiyonu.
 * @param {Function} props.onSubmit - Formu gönderme fonksiyonu.
 * @param {object | null} props.initialData - Düzenleme modu için başlangıç verisi.
 * @param {Array} props.connections - Seçim için mevcut veri tabanı bağlantıları.
 * @param {boolean} props.loading - Gönderme işleminin yüklenme durumu.
 */
const QueryEditorModal = ({ isOpen, onClose, onSubmit, initialData = null, connections = [], loading = false }) => {
    const [title, setTitle] = useState('');
    const [sqlQuery, setSqlQuery] = useState('');
    const [connectionId, setConnectionId] = useState('');
    const [sharingStatus, setSharingStatus] = useState('PRIVATE');
    
    const isEditMode = initialData !== null;

    useEffect(() => {
        // Modal açıldığında, düzenleme modunda ise formu doldur, değilse sıfırla.
        if (isOpen) {
            if (isEditMode) {
                setTitle(initialData.title || '');
                setSqlQuery(initialData.sql_query || '');
                setConnectionId(initialData.connection_id || '');
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

    return (
        <Modal 
            isOpen={isOpen} 
            onClose={onClose} 
            title={isEditMode ? 'Sorguyu Düzenle' : 'Yeni Sorgu Oluştur'}
        >
            <form onSubmit={handleSubmit}>
                <div className={styles.formGrid}>
                    <div className={styles.formGroup}>
                        <Input
                            label="Sorgu Başlığı"
                            value={title}
                            onChange={(e) => setTitle(e.target.value)}
                            required
                        />
                    </div>
                    
                    <div className={styles.formGroup}>
                         <Select
                            label="Veri Kaynağı"
                            value={connectionId}
                            onChange={(e) => setConnectionId(e.target.value)}
                            required
                            disabled={isEditMode} /* Düzenleme modunda bağlantı değiştirilemez. */
                        >
                            <option value="" disabled>Bir bağlantı seçin...</option>
                            {connections.map(conn => (
                                <option key={conn.id} value={conn.id}>{conn.title}</option>
                            ))}
                        </Select>
                    </div>

                    <div className={`${styles.formGroup} ${styles.fullWidth}`}>
                        <label className={styles.formLabel}>SQL Sorgusu</label>
                        {/* MİMARİ NOT: Burası gelecekte Monaco Editor veya Ace Editor gibi
                            bir kod editörü bileşeniyle değiştirilerek çok daha güçlü hale getirilebilir. */}
                        <textarea
                            value={sqlQuery}
                            onChange={(e) => setSqlQuery(e.target.value)}
                            rows="10"
                            required
                        />
                    </div>

                    <div className={styles.formGroup}>
                        <Select
                            label="Paylaşım Durumu"
                            value={sharingStatus}
                            onChange={(e) => setSharingStatus(e.target.value)}
                            required
                        >
                            {SHARING_OPTIONS.map(opt => (
                                <option key={opt.value} value={opt.value}>{opt.label}</option>
                            ))}
                        </Select>
                    </div>

                    <div className={styles.actions}>
                        <Button type="button" variant="secondary" onClick={onClose} disabled={loading}>
                            Vazgeç
                        </Button>
                        <Button type="submit" variant="primary" disabled={loading}>
                            {loading ? 'Kaydediliyor...' : (isEditMode ? 'Güncelle' : 'Oluştur')}
                        </Button>
                    </div>
                </div>
            </form>
        </Modal>
    );
};

export default QueryEditorModal;