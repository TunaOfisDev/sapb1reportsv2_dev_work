// path: frontend/src/components/NexusCore/containers/ReportPlayground/PivotBuilder/PivotRenderer.jsx

import React, { useMemo } from 'react';
import PropTypes from 'prop-types';
import styles from './PivotBuilder.module.scss'; 

/**
 * Agregasyon (Toplama) fonksiyonlarını yöneten yardımcı nesne.
 * GÜNCELLENDİ: AVG, MIN, MAX ve güvenlik kontrolleri eklendi.
 */

// Sayısal olmayan değerleri güvenli bir şekilde 0'a dönüştüren yardımcı fonksiyon
const safeParseFloat = (val) => parseFloat(val) || 0;

const aggregators = {
    sum: (arr) => arr.reduce((acc, val) => acc + safeParseFloat(val), 0),
    
    count: (arr) => arr.length,
    
    avg: (arr) => {
        const numericArr = arr.map(safeParseFloat);
        if (numericArr.length === 0) return 0; // Sıfıra bölme hatasını engelle
        const sum = numericArr.reduce((acc, val) => acc + val, 0);
        return sum / numericArr.length;
    },
    
    min: (arr) => {
        // Boş bir diziye Math.min uygulamak 'Infinity' döndürür, bu istenmez.
        if (arr.length === 0) return 0;
        const numericArr = arr.map(safeParseFloat);
        return Math.min(...numericArr);
    },
    
    max: (arr) => {
        // Boş bir diziye Math.max uygulamak '-Infinity' döndürür, bu da istenmez.
        if (arr.length === 0) return 0;
        const numericArr = arr.map(safeParseFloat);
        return Math.max(...numericArr);
    }
};


/**
 * Ham JSON verisini ve pivot tanımlarını alıp render edilebilir bir matrise dönüştüren ana iş motoru.
 * (Bu motor hala 1x1x1 modunda çalışıyor - Görev 2'de bunu değiştireceğiz)
 */
const processPivotData = (data, rows, columns, values) => {
    
    if (!rows.length || !columns.length || !values.length) {
        return { isReady: false };
    }

    // MVP Motoru: Hala ilk elemanları alıyor (Görev 2'de burası değişecek)
    const rowDef = rows[0];
    const colDef = columns[0]; 
    const valDef = values[0];

    const colIndexMap = data.columns.reduce((acc, colName, index) => {
        acc[colName] = index;
        return acc;
    }, {});

    const rowIndex = colIndexMap[rowDef.key];
    const colIndex = colIndexMap[colDef.key];
    const valIndex = colIndexMap[valDef.key];
    
    // GÜNCELLEME: Artık 'avg', 'min', 'max' seçilse bile doğru fonksiyonu bulacak
    const aggFn = aggregators[valDef.agg?.toLowerCase()] || aggregators.count; 

    const groupedData = new Map();
    const uniqueColKeys = new Set();
    const uniqueRowKeys = new Set();

    for (const rawRow of data.rows) {
        const rowKey = rawRow[rowIndex];
        const colKey = rawRow[colIndex];
        const value = rawRow[valIndex];

        uniqueRowKeys.add(rowKey);
        uniqueColKeys.add(colKey);

        if (!groupedData.has(rowKey)) {
            groupedData.set(rowKey, new Map());
        }
        if (!groupedData.get(rowKey).has(colKey)) {
            groupedData.get(rowKey).set(colKey, []);
        }

        groupedData.get(rowKey).get(colKey).push(value);
    }

    const rowHeaders = Array.from(uniqueRowKeys).sort();
    const colHeaders = Array.from(uniqueColKeys).sort();

    const matrix = [];
    const colTotals = new Array(colHeaders.length).fill(0);
    let grandTotal = 0;

    for (const rowKey of rowHeaders) {
        const matrixRow = [];
        let rowTotal = 0;
        const dataRow = groupedData.get(rowKey);

        for (let i = 0; i < colHeaders.length; i++) {
            const colKey = colHeaders[i];
            const cellValues = dataRow.get(colKey) || []; 
            const aggregatedValue = aggFn(cellValues); // aggFn artık avg/min/max'ı destekliyor

            matrixRow.push(aggregatedValue);
            rowTotal += (valDef.agg?.toLowerCase() === 'count') ? aggregatedValue : safeParseFloat(aggregatedValue); // Toplamları yaparken dikkatli olmalıyız
            
            // Sütun toplamlarını hesaplarken de agregasyon tipini dikkate almalıyız (avg toplamı almak mantıklı değil, ama şimdilik sum yapalım)
            // TODO: Genel Toplamlar için ayrı bir agregasyon mantığı gerekebilir (örn: AVG'lerin AVG'si değil, tüm verinin AVG'si)
            // Şimdilik basit tutuyoruz:
            colTotals[i] += aggregatedValue;
            grandTotal += aggregatedValue;
        }
        
        matrixRow.push(rowTotal); 
        matrix.push(matrixRow);
    }

    colTotals.push(grandTotal); 

    return {
        isReady: true,
        rowHeaders,
        colHeaders,
        matrix,
        colTotals,
        rowDimensionLabel: rowDef.label,
        colDimensionLabel: colDef.label,
    };
};

/**
 * PivotBuilder için ana render bileşeni.
 * (Render bloğunda değişiklik yok)
 */
const PivotRenderer = ({ data, pivotState }) => {
    
    const { rows, columns, values } = pivotState;

    const pivot = useMemo(() => {
        if (!data || !data.rows || data.rows.length === 0) {
            return { isReady: false };
        }
        return processPivotData(data, rows, columns, values);
    }, [data, rows, columns, values]);


    if (!pivot.isReady) {
        return (
            <div className={`${styles.pivotTableWrapper} ${styles.placeholder}`}>
                Pivot tablo oluşturmak için lütfen "Satırlar", "Sütunlar" ve "Değerler" alanlarına en az bir kolon sürükleyin.
            </div>
        );
    }

    // Render Mantığı (Değişiklik Yok)
    return (
        <div className={styles.pivotTableWrapper}>
            <table className={styles.pivotTable}>
                <thead>
                    <tr>
                        <th className={styles.headerCell}>
                            {pivot.rowDimensionLabel} / {pivot.colDimensionLabel}
                        </th>
                        {pivot.colHeaders.map(header => (
                            <th key={header} className={styles.headerCell}>{header}</th>
                        ))}
                        <th className={styles.totalCell}>TOPLAM</th>
                    </tr>
                </thead>
                <tbody>
                    {pivot.rowHeaders.map((rowHeader, rowIndex) => (
                        <tr key={rowHeader}>
                            <th className={styles.headerCell} scope="row">{rowHeader}</th>
                            {pivot.matrix[rowIndex].map((cellValue, cellIndex) => (
                                <td key={cellIndex} className={cellIndex === pivot.colHeaders.length ? styles.totalCell : styles.dataCell}>
                                    {/* Formatlama: AVG için ondalık basamak gerekebilir, şimdilik toLocaleString() yeterli. */}
                                    {Number(cellValue).toLocaleString(undefined, { maximumFractionDigits: 2 })}
                                </td>
                            ))}
                        </tr>
                    ))}
                </tbody>
                <tfoot>
                    <tr>
                        <th className={styles.totalCell}>GENEL TOPLAM</th>
                        {pivot.colTotals.map((total, index) => (
                            <th key={index} className={styles.totalCell}>
                                {Number(total).toLocaleString(undefined, { maximumFractionDigits: 2 })}
                            </th>
                        ))}
                    </tr>
                </tfoot>
            </table>
        </div>
    );
};

PivotRenderer.propTypes = {
    data: PropTypes.object,
    pivotState: PropTypes.shape({
        rows: PropTypes.array.isRequired,
        columns: PropTypes.array.isRequired,
        values: PropTypes.array.isRequired,
    }).isRequired,
};

export default PivotRenderer;