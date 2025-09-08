// frontend/src/components/NexusCore/containers/ReportPlayground/PivotBuilder/usePivotState.js 
import { useState, useEffect, useCallback, useRef } from 'react'; // useRef'i import et
import { useSensors, useSensor, PointerSensor } from '@dnd-kit/core';
import { arrayMove } from '@dnd-kit/sortable';
import { v4 as uuidv4 } from 'uuid';

export const usePivotState = (sourceColumns = [], initialConfig = {}, onChange) => {
    const [containers, setContainers] = useState({
        available: [], rows: [], columns: [], values: [], filters: [],
    });
    const [activeId, setActiveId] = useState(null);

    // --- NÖBETÇİ (GUARD REF) ---
    // Bu ref, sonsuz döngüyü kıran anahtarımızdır.
    // Amacı: Eğer state değişikliği 'initialConfig' prop'undan (yani Init Effect'ten) geliyorsa,
    // Report Effect'in bu değişikliği 'onChange' ile parent'a geri göndermesini engellemek.
    // Böylece 'Parent -> Child -> Parent' döngüsünü kırıyoruz.
    const isHydratingFromProps = useRef(false);
    // -------------------------

    // Bu stabildir, çünkü parent'taki (ReportPlayground) 'onChange' handler'ını
    // bir önceki adımda useCallback içine aldık.
    const memoizedOnChange = useCallback(onChange, [onChange]);

    // Prop'ları stabil string'lere dönüştürmek (bu zaten doğruydu)
    const stableInitialConfig = JSON.stringify(initialConfig);
    const stableSourceColumns = JSON.stringify(sourceColumns);


    // --- 1. ETKİ: BAŞLATMA (INIT EFFECT) ---
    // Sadece kaynak kolonlar veya ilk konfigürasyon (değer olarak) değiştiğinde çalışır.
    useEffect(() => {
        // console.log('%cINIT EFFECT ÇALIŞTI', 'color: #00AFFF');
        
        // Nöbetçiyi UYAR: "Raporlama yapma, şu an prop'lardan veri yüklüyorum!"
        isHydratingFromProps.current = true;

        const currentInitialConfig = JSON.parse(stableInitialConfig);
        const currentSourceColumns = JSON.parse(stableSourceColumns);

        const masterColumns = currentSourceColumns.map(colKey => ({ 
            id: uuidv4(), 
            key: colKey, 
            label: colKey 
        }));
        
        const newContainers = { available: [], rows: [], columns: [], values: [], filters: [] };
        const remainingColumns = [...masterColumns];

        const populateZone = (zoneKey, items) => {
            if (!Array.isArray(items)) return [];
            const populatedItems = [];
            items.forEach(itemConf => {
                const masterIndex = remainingColumns.findIndex(c => c.key === itemConf.key);
                if (masterIndex > -1) {
                    const [masterItem] = remainingColumns.splice(masterIndex, 1);
                    const finalItem = zoneKey === 'values' 
                        ? { ...masterItem, agg: itemConf.agg || 'SUM' } 
                        : masterItem;
                    populatedItems.push(finalItem);
                }
            });
            return populatedItems;
        };

        newContainers.rows = populateZone('rows', currentInitialConfig.rows || []);
        newContainers.columns = populateZone('columns', currentInitialConfig.columns || []);
        newContainers.values = populateZone('values', currentInitialConfig.values || []);
        newContainers.filters = populateZone('filters', currentInitialConfig.filters || []);
        newContainers.available = remainingColumns;
        
        setContainers(newContainers); // Bu, Report Effect'i tetikleyecek

    }, [stableSourceColumns, stableInitialConfig]); 


    // --- 2. ETKİ: RAPORLAMA (REPORT EFFECT) ---
    // Dahili 'containers' state'i değiştiğinde çalışır.
    useEffect(() => {
        // Nöbetçiyi KONTROL ET:
        if (isHydratingFromProps.current) {
            // Değişikliğin kaynağı Init Effect ise:
            // 1. Nöbetçiyi sıfırla (bir sonraki kullanıcı eylemine hazır ol).
            isHydratingFromProps.current = false;
            // 2. Parent'a rapor GÖNDERME ve döngüyü kır.
            // console.log('%cREPORT EFFECT - Hydration sebebiyle atlandı', 'color: #ff9900');
            return;
        }

        // Eğer buradaysak, değişiklik kullanıcıdan (drag/drop/remove) gelmiştir.
        // GÜVENLE PARENT'A RAPORLA.
        // console.log('%cREPORT EFFECT ÇALIŞTI (Kullanıcı Eylemi)', 'color: #00cc00');
        const pivotConfig = {
            rows: containers.rows.map(item => ({ key: item.key, label: item.label })),
            columns: containers.columns.map(item => ({ key: item.key, label: item.label })),
            values: containers.values.map(item => ({ key: item.key, label: item.label, agg: item.agg || 'SUM' })),
            filters: containers.filters.map(item => ({ key: item.key, label: item.label })),
        };
        memoizedOnChange(pivotConfig);

    }, [containers, memoizedOnChange]); // Bağımlılıklar doğru.

    const findContainerId = (id) => {
        if (id in containers) return id;
        return Object.keys(containers).find(key => containers[key].some(item => item.id === id));
    };

    // --- 3. EYLEM İŞLEYİCİLERİ (USER ACTIONS) ---
    // Bu fonksiyonlar 'isHydratingFromProps' ref'ine DOKUNMAZ.
    // 'setContainers' çağrıları, Report Effect'in çalışmasını tetikler
    // ve Report Effect nöbetçiyi 'false' göreceği için değişikliği raporlar.
    // Bu, tam olarak istediğimiz davranıştır.

    const handleDragStart = (event) => setActiveId(event.active.id);

    const handleDragEnd = (event) => {
        // ... (Bu fonksiyonun tüm içeriği aynı, değişiklik yok) ...
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
                
                if (overContainerId === 'values' && !movedItem.agg) {
                    movedItem.agg = 'SUM';
                }
                if (originalContainerId === 'values' && overContainerId !== 'values') {
                     delete movedItem.agg;
                }
                
                const overIndex = overItems.findIndex(item => item.id === over.id);
                if (overIndex !== -1) {
                    overItems.splice(overIndex, 0, movedItem);
                } else {
                    overItems.push(movedItem);
                }
                return { ...prev, [originalContainerId]: originalItems, [overContainerId]: overItems };
            });
        }
    };

    const handleRemoveItem = (itemId, containerId) => {
        // ... (Bu fonksiyonun tüm içeriği aynı, değişiklik yok) ...
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
        // ... (Bu fonksiyonun tüm içeriği aynı, değişiklik yok) ...
         setContainers(prev => ({
            ...prev,
            values: prev.values.map(item => item.id === itemId ? { ...item, agg: newAgg } : item)
        }));
    };

    const activeItem = activeId ? Object.values(containers).flat().find(item => item.id === activeId) : null;
    const activeItemContainerId = activeItem ? findContainerId(activeItem.id) : null;

    return {
        containers,
        sensors: useSensors(useSensor(PointerSensor, { activationConstraint: { distance: 5 } })),
        handleDragStart,
        handleDragEnd,
        handleRemoveItem,
        handleAggregationChange,
        activeItem,
        activeItemContainerId
    };
};