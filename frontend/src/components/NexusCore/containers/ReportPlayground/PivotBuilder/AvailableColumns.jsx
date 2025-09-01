// path: frontend/src/components/NexusCore/containers/ReportPlayground/PivotBuilder/AvailableColumns.jsx

import React from 'react';
import PropTypes from 'prop-types';
import { SortableContext, verticalListSortingStrategy } from '@dnd-kit/sortable';
import styles from './PivotBuilder.module.scss';
import DraggablePill from './DraggablePill';

const AvailableColumns = ({ id, items, onRemoveItem, onAggregationChange }) => {
    return (
        <div className={styles.availableColumnsContainer}>
            <h4 className={styles.dropZoneTitle}>Kullanılabilir Kolonlar</h4>
            <div className={styles.dropZoneContent}>
                <SortableContext items={items.map(item => item.id)} strategy={verticalListSortingStrategy}>
                    {items.length > 0 ? (
                        items.map(item => (
                            <DraggablePill key={item.id} id={item.id} label={item.label} onRemove={onRemoveItem}
                                zoneId={id} onAggregationChange={onAggregationChange} isAvailableZone={true} />
                        ))
                    ) : (<div className={styles.dropZonePlaceholder}>Tüm kolonlar kullanılıyor</div>)}
                </SortableContext>
            </div>
        </div>
    );
};
AvailableColumns.propTypes = {
    id: PropTypes.string.isRequired,
    items: PropTypes.array.isRequired,
    onRemoveItem: PropTypes.func.isRequired,
    onAggregationChange: PropTypes.func.isRequired,
};
export default AvailableColumns;