// path: frontend/src/components/NexusCore/containers/ReportPlayground/PivotBuilder/DroppableZone.jsx

import React from 'react';
import PropTypes from 'prop-types';
import { useDroppable } from '@dnd-kit/core';
import { SortableContext, verticalListSortingStrategy } from '@dnd-kit/sortable';
import styles from './PivotBuilder.module.scss';
import DraggablePill from './DraggablePill';

const DroppableZone = ({ id, title, items, onRemoveItem, onAggregationChange, zoneId }) => {
    const { setNodeRef, isOver } = useDroppable({ id });
    const zoneClasses = `${styles.dropZone} ${isOver ? styles.isOver : ''}`;
    return (
        <div ref={setNodeRef} className={zoneClasses}>
            <h4 className={styles.dropZoneTitle}>{title}</h4>
            <div className={styles.dropZoneContent}>
                <SortableContext items={items.map(item => item.id)} strategy={verticalListSortingStrategy}>
                    {items.length > 0 ? (
                        items.map(item => (
                            <DraggablePill key={item.id} id={item.id} label={item.label} onRemove={onRemoveItem}
                                zoneId={zoneId} aggregation={item.agg} onAggregationChange={onAggregationChange} />
                        ))
                    ) : ( <div className={styles.dropZonePlaceholder}>Kolonları buraya sürükleyin</div> )}
                </SortableContext>
            </div>
        </div>
    );
};
DroppableZone.propTypes = {
    id: PropTypes.string.isRequired,
    title: PropTypes.string.isRequired,
    items: PropTypes.array.isRequired,
    onRemoveItem: PropTypes.func.isRequired,
    onAggregationChange: PropTypes.func.isRequired,
    zoneId: PropTypes.string.isRequired,
};
export default DroppableZone;