// path: frontend/src/components/NexusCore/containers/ReportPlayground/PivotBuilder/index.jsx

import React from 'react';
import PropTypes from 'prop-types';
import { DndContext, DragOverlay, closestCenter } from '@dnd-kit/core';
import styles from './PivotBuilder.module.scss';
import AvailableColumns from './AvailableColumns';
import DroppableZone from './DroppableZone';
import DraggablePill from './DraggablePill';
import { usePivotState } from './usePivotState';

// ### ADIM 1: Motorumuzu (Renderer) içeri aktarıyoruz ###
import PivotRenderer from './PivotRenderer';

// ### ADIM 2: Bileşenin artık ham veriyi (data) prop olarak almasını sağlıyoruz ###
const PivotBuilder = ({ sourceColumns, data, onChange, initialConfig }) => {
    // Bu hook bize hem sürükle-bırak durumu hem de pivot yapılandırmasını (containers) verir
    const { 
        containers, 
        sensors, 
        handleDragStart, 
        handleDragEnd, 
        handleRemoveItem, 
        handleAggregationChange, 
        activeItem, 
        activeItemContainerId 
    } = usePivotState(sourceColumns, initialConfig, onChange);

    // pivotState, renderer'ımızın beklediği { rows, cols, values } vb. içeren nesnedir.
    // 'containers' nesnesi tam olarak bu yapıdadır.
    const pivotState = containers;

    return (
        <DndContext sensors={sensors} onDragStart={handleDragStart} onDragEnd={handleDragEnd} collisionDetection={closestCenter}>
            <div className={styles.pivotBuilderContainer}>
                {/* 1. Sütun: Kullanılabilir Kolonlar */}
                <AvailableColumns 
                    id="available" 
                    items={containers.available} 
                    onRemoveItem={handleRemoveItem} 
                    onAggregationChange={handleAggregationChange} 
                />
                
                {/* 2. Sütun: Bırakma Alanları VE Render Çıktısı */}
                <div className={styles.pivotDropZones}>
                    {/* Alanlar */}
                    <DroppableZone id="filters" title="Filtreler" items={containers.filters} onRemoveItem={handleRemoveItem} zoneId="filters" onAggregationChange={handleAggregationChange}/>
                    <div className={styles.pivotRowAndCol}>
                        <DroppableZone id="rows" title="Satırlar" items={containers.rows} onRemoveItem={handleRemoveItem} zoneId="rows" onAggregationChange={handleAggregationChange} />
                        <DroppableZone id="columns" title="Sütunlar" items={containers.columns} onRemoveItem={handleRemoveItem} zoneId="columns" onAggregationChange={handleAggregationChange}/>
                    </div>
                    <DroppableZone id="values" title="Değerler" items={containers.values} onRemoveItem={handleRemoveItem} zoneId="values" onAggregationChange={handleAggregationChange} />

                    {/* ### ADIM 3: Motoru Monte Et! ###
                      İşte pivot çıktısını tam da konfigürasyon alanının altına render ediyoruz.
                      Gerekli iki prop'u (data ve pivotState) buraya bağlıyoruz.
                    */}
                    <PivotRenderer data={data} pivotState={pivotState} />
                
                </div>
            </div>

            {/* Sürükleme efekti için bindirme (overlay) */}
            <DragOverlay>
                {activeItem ? (
                    <DraggablePill 
                        id={activeItem.id} 
                        label={activeItem.label} 
                        onRemove={() => {}} 
                        zoneId={activeItemContainerId} 
                        aggregation={activeItem.agg} 
                        onAggregationChange={() => {}} 
                        isAvailableZone={activeItemContainerId === 'available'} 
                    />
                ) : null}
            </DragOverlay>
        </DndContext>
    );
};

PivotBuilder.propTypes = {
    sourceColumns: PropTypes.array,
    data: PropTypes.object, // ### YENİ: Ham veriyi almak için bu prop'u ekledik.
    onChange: PropTypes.func.isRequired,
    initialConfig: PropTypes.object,
};

export default PivotBuilder;