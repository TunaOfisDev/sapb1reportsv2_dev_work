// path: frontend/src/components/NexusCore/containers/ReportPlayground/PivotBuilder/index.jsx

import React from 'react';
import PropTypes from 'prop-types';
import { DndContext, DragOverlay, closestCenter } from '@dnd-kit/core';
import styles from './PivotBuilder.module.scss';
import AvailableColumns from './AvailableColumns';
import DroppableZone from './DroppableZone';
import DraggablePill from './DraggablePill';
import { usePivotState } from './usePivotState';

const PivotBuilder = ({ sourceColumns, onChange, initialConfig }) => {
    const { containers, sensors, handleDragStart, handleDragEnd, handleRemoveItem, handleAggregationChange, activeItem, activeItemContainerId } = usePivotState(sourceColumns, initialConfig, onChange);
    return (
        <DndContext sensors={sensors} onDragStart={handleDragStart} onDragEnd={handleDragEnd} collisionDetection={closestCenter}>
            <div className={styles.pivotBuilderContainer}>
                <AvailableColumns id="available" items={containers.available} onRemoveItem={handleRemoveItem} onAggregationChange={handleAggregationChange} />
                <div className={styles.pivotDropZones}>
                    <DroppableZone id="filters" title="Filtreler" items={containers.filters} onRemoveItem={handleRemoveItem} zoneId="filters" onAggregationChange={handleAggregationChange}/>
                    <div className={styles.pivotRowAndCol}>
                        <DroppableZone id="rows" title="Satırlar" items={containers.rows} onRemoveItem={handleRemoveItem} zoneId="rows" onAggregationChange={handleAggregationChange} />
                        <DroppableZone id="columns" title="Sütunlar" items={containers.columns} onRemoveItem={handleRemoveItem} zoneId="columns" onAggregationChange={handleAggregationChange}/>
                    </div>
                    <DroppableZone id="values" title="Değerler" items={containers.values} onRemoveItem={handleRemoveItem} zoneId="values" onAggregationChange={handleAggregationChange} />
                </div>
            </div>
            <DragOverlay>
                {activeItem ? (
                    <DraggablePill id={activeItem.id} label={activeItem.label} onRemove={() => {}} zoneId={activeItemContainerId} aggregation={activeItem.agg} onAggregationChange={() => {}} isAvailableZone={activeItemContainerId === 'available'} />
                ) : null}
            </DragOverlay>
        </DndContext>
    );
};
PivotBuilder.propTypes = {
    sourceColumns: PropTypes.array,
    onChange: PropTypes.func.isRequired,
    initialConfig: PropTypes.object,
};
export default PivotBuilder;