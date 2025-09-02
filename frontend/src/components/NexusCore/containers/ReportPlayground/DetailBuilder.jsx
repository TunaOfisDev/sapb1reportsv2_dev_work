// path: frontend/src/components/NexusCore/containers/ReportPlayground/DetailBuilder.jsx

import React, { useState, useEffect } from 'react';
import PropTypes from 'prop-types';
import { DndContext, closestCenter, PointerSensor, useSensor, useSensors } from '@dnd-kit/core';
import { SortableContext, useSortable, arrayMove, verticalListSortingStrategy } from '@dnd-kit/sortable';
import { v4 as uuidv4 } from 'uuid';
import styles from './ReportPlayground.module.scss';

// İkonlar ve Ortak Bileşenler
import { MoreVertical, Eye, EyeOff } from 'react-feather';
import Input from '../../components/common/Input/Input';
import Table from '../../components/common/Table/Table';

// Her bir kolonu yöneten, kendi içinde interaktif olan alt bileşen
const SortableColumnItem = ({ col, onUpdate }) => {
    const { attributes, listeners, setNodeRef, transform, transition, isDragging } = useSortable({ id: col.id });
    const style = {
        transform: transform ? `translate3d(0, ${transform.y}px, 0)` : undefined,
        transition,
        opacity: isDragging ? 0.5 : 1,
    };

    return (
        <li ref={setNodeRef} style={style} className={`${styles.columnManagerItem} ${isDragging ? styles.dragging : ''}`}>
            <span {...listeners} {...attributes} className={styles.dragHandle}><MoreVertical /></span>
            <div className={styles.columnEditor}>
                <Input 
                    id={`label-${col.id}`}
                    value={col.label}
                    onChange={(e) => onUpdate(col.key, { label: e.target.value })}
                />
            </div>
            <button 
                className={`${styles.visibilityToggle} ${col.visible ? styles.visible : ''}`}
                onClick={() => onUpdate(col.key, { visible: !col.visible })}
                title={col.visible ? 'Kolonu Gizle' : 'Kolonu Göster'}
            >
                {col.visible ? <Eye size={18} /> : <EyeOff size={18} />}
            </button>
        </li>
    );
};

const DetailBuilder = ({ sourceData, config, setConfig }) => {
    const [reportColumns, setReportColumns] = useState(config.columns || []);

    // Kaynak veri ilk geldiğinde veya değiştiğinde, kolon listesini başlat.
    useEffect(() => {
        if (sourceData?.columns) {
            setReportColumns(sourceData.columns.map(colName => ({
                id: uuidv4(),
                key: colName,
                label: colName,
                visible: true,
            })));
        }
    }, [sourceData]);

    // `reportColumns` state'i her değiştiğinde, ana orkestratöre haber ver.
    useEffect(() => {
        setConfig(prev => ({ ...prev, columns: reportColumns }));
    }, [reportColumns, setConfig]);

    const handleColumnUpdate = (key, newProps) => {
        setReportColumns(items => items.map(col => 
            col.key === key ? { ...col, ...newProps } : col
        ));
    };

    const sensors = useSensors(useSensor(PointerSensor, { activationConstraint: { distance: 5 } }));

    const handleDragEnd = (event) => {
        const { active, over } = event;
        if (over && active.id !== over.id) {
            setReportColumns((items) => {
                const oldIndex = items.findIndex(item => item.id === active.id);
                const newIndex = items.findIndex(item => item.id === over.id);
                return arrayMove(items, oldIndex, newIndex);
            });
        }
    };

    const getPreviewData = () => {
        if (!sourceData || !sourceData.rows || reportColumns.length === 0) return null;

        const visibleColumns = reportColumns.filter(c => c.visible);
        if (visibleColumns.length === 0) return { columns: [], rows: [] };

        const finalColumns = visibleColumns.map(c => c.label);
        const colIndexMap = sourceData.columns.reduce((acc, colName, index) => { acc[colName] = index; return acc; }, {});
        const finalColIndices = visibleColumns.map(c => colIndexMap[c.key]);
        const finalRows = sourceData.rows.map(row => finalColIndices.map(index => row[index]));

        return { columns: finalColumns, rows: finalRows };
    };

    return (
        <DndContext sensors={sensors} onDragEnd={handleDragEnd} collisionDetection={closestCenter}>
            <div className={styles.panel}>
                <h3 className={styles.panelTitle}>Kolon Yöneticisi</h3>
                <div className={styles.panelContent}>
                    <SortableContext items={reportColumns.map(c => c.id)} strategy={verticalListSortingStrategy}>
                        <ul className={styles.columnManagerList}>
                            {reportColumns.map(col => (
                                <SortableColumnItem key={col.id} col={col} onUpdate={handleColumnUpdate} />
                            ))}
                        </ul>
                    </SortableContext>
                </div>
            </div>
            <div className={styles.panel}>
                 <h3 className={styles.panelTitle}>Canlı Önizleme</h3>
                 <div className={styles.tableWrapper}>
                    <Table data={getPreviewData()} />
                 </div>
            </div>
        </DndContext>
    );
};

DetailBuilder.propTypes = {
    sourceData: PropTypes.object,
    config: PropTypes.object.isRequired,
    setConfig: PropTypes.func.isRequired,
};

export default DetailBuilder;