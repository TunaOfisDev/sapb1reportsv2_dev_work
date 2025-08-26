// path: frontend/src/components/NexusCore/containers/VirtualTableWorkspace/VirtualTableList.jsx
import React from 'react';
import PropTypes from 'prop-types';
import { PlayCircle, Edit, Trash2, Database, Lock, Eye } from 'react-feather';
import styles from './VirtualTableList.module.scss';
import Button from '../../components/common/Button/Button';
import { formatSharingStatus } from '../../utils/formatters';

const statusIcons = {
    lock: <Lock size={14} />,
    eye: <Eye size={14} />,
};

const VirtualTableList = ({ tables = [], onExecute, onEdit, onDelete }) => {
    if (tables.length === 0) {
        return <p className={styles.emptyMessage}>Henüz oluşturulmuş bir sorgu yok. "Yeni Sorgu Oluştur" butonu ile başlayabilirsiniz.</p>;
    }

    return (
        <ul className={styles.list}>
            {tables.map(table => {
                const status = formatSharingStatus(table.sharing_status);
                const StatusIcon = statusIcons[status.icon] || null;

                return(
                    <li key={table.id} className={styles.listItem}>
                        <div className={styles.info}>
                            <h3 className={styles.title}>{table.title}</h3>
                            <div className={styles.details}>
                                <span className={styles.detailItem}>
                                    <Database size={14} /> {table.connection_display}
                                </span>
                                <span className={styles.detailItem}>
                                    {StatusIcon} {status.text}
                                </span>
                            </div>
                        </div>
                        <div className={styles.actions}>
                            <Button variant="secondary" onClick={() => onExecute(table)} IconComponent={PlayCircle}>
                                Çalıştır
                            </Button>
                            <Button variant="secondary" onClick={() => onEdit(table)} IconComponent={Edit}>
                                Düzenle
                            </Button>
                            <Button variant="danger" onClick={() => onDelete(table)} IconComponent={Trash2}>
                                Sil
                            </Button>
                        </div>
                    </li>
                );
            })}
        </ul>
    );
};

VirtualTableList.propTypes = {
    tables: PropTypes.array.isRequired,
    onExecute: PropTypes.func.isRequired,
    onEdit: PropTypes.func.isRequired,
    onDelete: PropTypes.func.isRequired,
};

export default VirtualTableList;