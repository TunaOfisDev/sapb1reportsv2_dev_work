// path: frontend/src/components/NexusCore/containers/ReportPlayground/ReportCanvas.jsx
import React from 'react';
import PropTypes from 'prop-types';
// ### DÜZELTME: `useSortable`'ı `@dnd-kit/sortable`'dan, diğerlerini `@dnd-kit/core`'dan alıyoruz. ###
import { useDroppable } from '@dnd-kit/core';
import { useSortable, SortableContext, verticalListSortingStrategy } from '@dnd-kit/sortable';
import styles from './ReportPlayground.module.scss';
import { X } from 'react-feather';

// Her bir sıralanabilir kolon başlığını temsil eden alt bileşen
const SortableColumnHeader = ({ col, selected, onClick, onRemove }) => {
    // `useSortable` hook'u artık doğru yerden import edildiği için çalışacaktır.
    const { attributes, listeners, setNodeRef, transform, transition } = useSortable({ id: col.id });

    const style = {
        transform: transform ? `translate3d(${transform.x}px, ${transform.y}px, 0)` : undefined,
        transition,
    };

    return (
        <th 
            ref={setNodeRef} 
            style={style} 
            {...attributes} 
            {...listeners}
            onClick={onClick}
            className={selected ? styles.active : ''}
            title={`Orijinal Ad: ${col.key}`}
        >
            <div className={styles.thContent}>
                <span>{col.label}</span>
                <button
                  className={styles.removeColumnBtn}
                  onClick={(e) => { e.stopPropagation(); onRemove(col.key); }}
                  title="Kolonu rapordan kaldır"
                >
                  <X size={14} />
                </button>
            </div>
        </th>
    );
};


const ReportCanvas = ({ columns, data, onColumnClick, selectedColumnKey, onColumnRemove }) => {
    const { setNodeRef } = useDroppable({ id: 'canvas-drop-area' });
    const previewRows = data.rows ? data.rows.slice(0, 5) : [];
    const colIndexMap = data.columns ? data.columns.reduce((acc, colName, index) => { acc[colName] = index; return acc; }, {}) : {};
    const visibleColumns = columns.filter(col => col.visible);

    return (
        <div ref={setNodeRef} className={`${styles.panel} ${styles.reportCanvas}`}>
            <h3 className={styles.panelTitle}>Rapor Önizlemesi</h3>
            <div className={styles.panelContent}>
                {columns.length === 0 ? (
                    <div className={styles.canvasPlaceholder}>Rapor oluşturmak için soldaki listeden kolonları buraya sürükleyin veya çift tıklayın.</div>
                ) : (
                    <div className={styles.previewTableWrapper}>
                        <table className={styles.previewTable}>
                            <thead>
                                <tr>
                                    {/* SortableContext'i ReportPlayground/index.jsx'e taşıdık, buradaki gereksiz sarmalayıcıyı kaldırdık. */}
                                    {visibleColumns.map(col => (
                                        <SortableColumnHeader
                                            key={col.id}
                                            col={col}
                                            selected={selectedColumnKey === col.key}
                                            onClick={() => onColumnClick(col.key)}
                                            onRemove={onColumnRemove}
                                        />
                                    ))}
                                </tr>
                            </thead>
                            <tbody>
                                {previewRows.map((row, rowIndex) => (
                                    <tr key={rowIndex}>
                                        {visibleColumns.map(col => (
                                            <td key={col.key}>{String(row[colIndexMap[col.key]] ?? '')}</td>
                                        ))}
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                )}
            </div>
        </div>
    );
};

ReportCanvas.propTypes = {
  columns: PropTypes.array.isRequired,
  data: PropTypes.object,
  onColumnClick: PropTypes.func.isRequired,
  selectedColumnKey: PropTypes.string,
  onColumnRemove: PropTypes.func.isRequired, // ### YENİ PROP ###
};

export default ReportCanvas;