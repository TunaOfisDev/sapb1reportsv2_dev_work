// path: frontend/src/components/NexusCore/containers/ReportPlayground/PivotBuilder/DraggablePill.jsx

import React from 'react';
import PropTypes from 'prop-types';
import { useSortable } from '@dnd-kit/sortable';
import { CSS } from '@dnd-kit/utilities';
import { MoreVertical, X } from 'react-feather';
import styles from './PivotBuilder.module.scss';

const AGGREGATION_OPTIONS = ['SUM', 'COUNT', 'AVG', 'MIN', 'MAX'];
const DraggablePill = ({ id, label, onRemove, zoneId, aggregation, onAggregationChange, isAvailableZone = false }) => {
    const { attributes, listeners, setNodeRef, transform, transition, isDragging } = useSortable({ id });
    
    console.log(`Pill ID: ${id}`, { listeners });

    const style = {
        transform: CSS.Transform.toString(transform),
        transition,
        opacity: isDragging ? 0.5 : 1,
    };
    const handleAggChange = (e) => {
        e.stopPropagation();
        onAggregationChange(id, e.target.value);
    };
    return (
        <div ref={setNodeRef} style={style} className={`${styles.draggablePill} ${isDragging ? styles.dragging : ''}`}>
            <span {...listeners} {...attributes} className={styles.dragHandle}><MoreVertical size={18} /></span>
            {zoneId === 'values' && !isAvailableZone ? (
                <div className={styles.pillContent}>
                    <select className={styles.aggSelect} value={aggregation} onChange={handleAggChange} onClick={(e) => e.stopPropagation()}>
                        {AGGREGATION_OPTIONS.map(opt => <option key={opt} value={opt}>{opt}</option>)}
                    </select>
                    <span className={styles.pillLabel}>({label})</span>
                </div>
            ) : (<span className={styles.pillLabel}>{label}</span>)}
            {!isAvailableZone && (
                <button className={styles.removeBtn} onClick={() => onRemove(id, zoneId)} title="Kolonu kaldır">
                    <X size={16} />
                </button>
            )}
        </div>
    );
};
DraggablePill.propTypes = {
    id: PropTypes.string.isRequired,
    label: PropTypes.string.isRequired,
    onRemove: PropTypes.func.isRequired,
    zoneId: PropTypes.string.isRequired,
    aggregation: PropTypes.string,
    onAggregationChange: PropTypes.func,
    isAvailableZone: PropTypes.bool,
};
export default DraggablePill;