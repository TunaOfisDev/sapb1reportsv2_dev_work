// path: frontend/src/components/NexusCore/containers/ReportPlayground/PivotBuilder/usePivotState.js

import { useState, useEffect, useCallback } from 'react';
import { useSensors, useSensor, PointerSensor } from '@dnd-kit/core';
import { arrayMove } from '@dnd-kit/sortable';
import { v4 as uuidv4 } from 'uuid';

export const usePivotState = (sourceColumns = [], initialConfig = {}, onChange) => {
    const [containers, setContainers] = useState({
        available: [], rows: [], columns: [], values: [], filters: [],
    });
    const [activeId, setActiveId] = useState(null);
    const memoizedOnChange = useCallback(onChange, [onChange]);

    useEffect(() => {
        console.log(`%cPIVOT STATE useEffect TETİKLENDİ - ${new Date().toLocaleTimeString()}`, 'color: #ff00ff; font-weight: bold;');
        const masterColumns = sourceColumns.map(col => ({ id: uuidv4(), key: col, label: col }));
        const newContainers = { available: [], rows: [], columns: [], values: [], filters: [] };
        const remainingColumns = [...masterColumns];

        const populateZone = (zoneKey, items) => {
            if (!Array.isArray(items)) return [];
            const populatedItems = [];
            items.forEach(itemConf => {
                const masterIndex = remainingColumns.findIndex(c => c.key === itemConf.key);
                if (masterIndex > -1) {
                    const [masterItem] = remainingColumns.splice(masterIndex, 1);
                    const finalItem = zoneKey === 'values' ? { ...masterItem, agg: itemConf.agg || 'SUM' } : masterItem;
                    populatedItems.push(finalItem);
                }
            });
            return populatedItems;
        };

        newContainers.rows = populateZone('rows', initialConfig.rows);
        newContainers.columns = populateZone('columns', initialConfig.columns);
        newContainers.values = populateZone('values', initialConfig.values);
        newContainers.filters = populateZone('filters', initialConfig.filters);
        newContainers.available = remainingColumns;
        setContainers(newContainers);
    }, [sourceColumns, initialConfig]);

    useEffect(() => {
        const pivotConfig = {
            rows: containers.rows.map(item => ({ key: item.key, label: item.label })),
            columns: containers.columns.map(item => ({ key: item.key, label: item.label })),
            values: containers.values.map(item => ({ key: item.key, label: item.label, agg: item.agg || 'SUM' })),
            filters: containers.filters.map(item => ({ key: item.key, label: item.label })),
        };
        memoizedOnChange(pivotConfig);
    }, [containers, memoizedOnChange]);

    const findContainerId = (id) => {
        if (id in containers) return id;
        return Object.keys(containers).find(key => containers[key].some(item => item.id === id));
    };

    const handleDragStart = (event) => setActiveId(event.active.id);
    const handleDragEnd = (event) => {
        const { active, over } = event;
        setActiveId(null);
        if (!over) return;
        const originalContainerId = findContainerId(active.id);
        const overContainerId = findContainerId(over.id) || over.id;
        if (!originalContainerId || !overContainerId) return;
        if (originalContainerId === overContainerId) {
            if (active.id !== over.id) {
                setContainers(prev => {
                    const containerItems = prev[originalContainerId];
                    const oldIndex = containerItems.findIndex(item => item.id === active.id);
                    const newIndex = containerItems.findIndex(item => item.id === over.id);
                    if (oldIndex === -1 || newIndex === -1) return prev;
                    return { ...prev, [originalContainerId]: arrayMove(containerItems, oldIndex, newIndex) };
                });
            }
        } else {
            setContainers(prev => {
                const originalItems = [...prev[originalContainerId]];
                const overItems = [...prev[overContainerId]];
                const activeIndex = originalItems.findIndex(item => item.id === active.id);
                if (activeIndex === -1) return prev;
                const [movedItem] = originalItems.splice(activeIndex, 1);
                if (overContainerId === 'values' && !movedItem.agg) movedItem.agg = 'SUM';
                if (originalContainerId === 'values' && overContainerId !== 'values') delete movedItem.agg;
                const overIndex = overItems.findIndex(item => item.id === over.id);
                if (overIndex !== -1) overItems.splice(overIndex, 0, movedItem);
                else overItems.push(movedItem);
                return { ...prev, [originalContainerId]: originalItems, [overContainerId]: overItems };
            });
        }
    };
    const handleRemoveItem = (itemId, containerId) => {
        const itemToRemove = containers[containerId].find(item => item.id === itemId);
        if (!itemToRemove) return;
        const { agg, ...restOfItem } = itemToRemove;
        setContainers(prev => ({
            ...prev,
            [containerId]: prev[containerId].filter(item => item.id !== itemId),
            available: [...prev.available, restOfItem],
        }));
    };
    const handleAggregationChange = (itemId, newAgg) => {
        setContainers(prev => ({
            ...prev,
            values: prev.values.map(item => item.id === itemId ? { ...item, agg: newAgg } : item)
        }));
    };
    const activeItem = activeId ? Object.values(containers).flat().find(item => item.id === activeId) : null;
    const activeItemContainerId = activeItem ? findContainerId(activeItem.id) : null;
    return {
        containers, sensors: useSensors(useSensor(PointerSensor, { activationConstraint: { distance: 5 } })),
        handleDragStart, handleDragEnd, handleRemoveItem, handleAggregationChange, activeItem, activeItemContainerId
    };
};