// path: frontend/src/components/NexusCore/containers/ReportPlayground/AvailableColumns.jsx
import React from 'react';
import PropTypes from 'prop-types';
import { useDraggable } from '@dnd-kit/core';
import styles from './ReportPlayground.module.scss';
import { MoreVertical } from 'react-feather';

// Her bir sürüklenebilir kolonu temsil eden alt bileşen
const DraggableColumn = ({ columnName }) => {
    const { attributes, listeners, setNodeRef, transform } = useDraggable({
        id: columnName, // Sürüklenebilir nesnenin benzersiz kimliği
    });

    const style = transform ? {
        transform: `translate3d(${transform.x}px, ${transform.y}px, 0)`,
    } : undefined;

    return (
        <li 
            ref={setNodeRef} 
            style={style} 
            {...listeners} 
            {...attributes}
            className={styles.columnItem}
        >
            <MoreVertical className={styles.dragHandle} size={18} />
            <span className={styles.columnName}>{columnName}</span>
        </li>
    );
};

DraggableColumn.propTypes = { columnName: PropTypes.string.isRequired };

const AvailableColumns = ({ columns }) => {
  return (
    <div className={`${styles.panel} ${styles.availableColumns}`}>
      <h3 className={styles.panelTitle}>Kullanılabilir Kolonlar</h3>
      <div className={styles.panelContent}>
        {columns.length === 0 ? (
          <div className={styles.placeholder}>Kaynak veride kolon bulunamadı.</div>
        ) : (
          <ul className={styles.columnList}>
            {columns.map(columnName => (
              <DraggableColumn key={columnName} columnName={columnName} />
            ))}
          </ul>
        )}
      </div>
    </div>
  );
};

AvailableColumns.propTypes = { columns: PropTypes.arrayOf(PropTypes.string).isRequired };
export default AvailableColumns;