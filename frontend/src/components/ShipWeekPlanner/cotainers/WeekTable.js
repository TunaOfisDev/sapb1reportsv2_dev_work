// frontend/src/components/ShipWeekPlanner/containers/WeekTable.js
import React, { useState, useEffect, useMemo, useCallback } from 'react';
import { TextField, Button, Typography } from '@mui/material';
import DatePicker from "react-datepicker";
import "react-datepicker/dist/react-datepicker.css";
import { registerLocale, setDefaultLocale } from "react-datepicker";
import tr from 'date-fns/locale/tr';
import dayjs from 'dayjs';
import customParseFormat from 'dayjs/plugin/customParseFormat';
import isoWeek from 'dayjs/plugin/isoWeek';
import groupByDayOfWeek from '../utils/groupByDayOfWeek';
import PaintThePlan from '../utils/paintThePlan';
import ExpandableCell from '../components/ExpandableCell';
import CopyToForm from '../components/CopyToForm';
import '../css/ShipWeekPlanner.css';
import '../css/datePicker.css';

dayjs.extend(customParseFormat);
dayjs.extend(isoWeek);

registerLocale('tr', tr);
setDefaultLocale('tr');

const WeekTable = ({
    orders,
    loading,
    error,
    modifyShipmentOrder,
    addShipmentOrder,
    saveSelectedColor,
    loadShipmentOrders,
    formatDateForBackend,
    selectedWeek,
    shouldAddNewRow,
    onNewRowAdded,
    onDataChange,
    filterStatus
}) => {
    const [editableData, setEditableData] = useState({});
    const [newRow, setNewRow] = useState(null);

    // Filtrelenmis veriyi elde etmek icin
    const getFilteredData = useCallback(() => {
        if (filterStatus === 'Hepsi') {
            return orders;
        }
        return orders.filter(order => order.order_status === filterStatus);
    }, [orders, filterStatus]);

    // Editable veriyi guncelle
    useEffect(() => {
        const filteredData = getFilteredData();
        setEditableData(filteredData.reduce((acc, order) => ({
            ...acc,
            [order.id]: {
                ...order,
                order_date: parseDate(order.order_date),
                shipment_date: parseDate(order.shipment_date),
                planned_date_real: parseDate(order.planned_date_real),
                planned_date_mirror: parseDate(order.planned_date_mirror)
            }
        }), {}));
        onDataChange(filteredData);
    }, [getFilteredData, onDataChange]);

    const columns = useMemo(() => [
        { Header: 'Gun', accessor: 'day_of_week', editable: false },
        { Header: 'Statu', accessor: 'order_status', editable: false },
        { Header: 'SiparisNo', accessor: 'order_number', editable: true },
        { Header: 'MuteriAd', accessor: 'customer_name', editable: true },
        { Header: 'SiparisTarihi', accessor: 'order_date', isDate: true, editable: true },
        { Header: 'SevkTarihi', accessor: 'shipment_date', isDate: true, editable: true },
        { Header: 'GercekPlanTarih', accessor: 'planned_date_real', isDate: true, editable: false },
        { Header: 'Hafta', accessor: 'planned_date_week', editable: false },
        { Header: 'PlanTarih', accessor: 'planned_date_mirror', isDate: true, editable: true },
        { Header: 'Satici', accessor: 'sales_person', editable: true },
        { Header: 'SevkAdres', accessor: 'shipment_details', editable: true },
        { Header: 'SevkNotlari', accessor: 'shipment_notes', editable: true },
    ], []);

    const columnStyles = useMemo(() => ({
        day_of_week: { width: '75px', minWidth: '75px' },
        order_status: { width: '50px', minWidth: '50px' },
        order_number: { width: '60px', minWidth: '60px' },
        customer_name: { width: '145px', minWidth: '145px' },
        order_date: { width: '105px', minWidth: '105px' },
        shipment_date: { width: '105px', minWidth: '105px' },
        planned_date_real: { width: '110px', minWidth: '110px' },
        planned_date_week: { width: '25px', minWidth: '25px' },
        planned_date_mirror: { width: '105px', minWidth: '105px' },
        sales_person: { width: '75px', minWidth: '75px' },
        shipment_details: { width: '135px', minWidth: '135px' },
        shipment_notes: { width: '135px', minWidth: '135px' },
        operations: { width: '150px', minWidth: '150px' }
    }), []);

    const handleCellChange = (rowId, field, value) => {
        const column = columns.find(col => col.accessor === field);
        if (column?.editable === false) return;

        if (rowId === 'new') {
            setNewRow(prev => ({ ...prev, [field]: value }));
        } else {
            setEditableData(prev => ({
                ...prev,
                [rowId]: { ...prev[rowId], [field]: value }
            }));
        }
    };

    // handleCopyRow fonksiyonunu ekle
    const handleCopyRow = (copiedData) => {
        setNewRow(copiedData);
    };

    const handleSaveRow = async (rowId) => {
        const rowData = rowId === 'new' ? newRow : editableData[rowId];
        
        if (!rowData.order_number || rowData.order_number.trim() === "") {
            alert('Lutfen Siparis Numarasini girin.');
            return;
        }
        
        if (rowId === 'new' && !rowData.planned_date_mirror) {
            alert('Yeni kayit icin lutfen Plan Tarihini girin.');
            return;
        }
        
        const updatedData = {
            ...rowData,
            order_status: rowData.order_status || "Acik",
            planned_date_week: rowData.planned_date_week || (rowData.order_date ? dayjs(rowData.order_date).isoWeek() : null),
            order_date: rowData.order_date ? formatDateForBackend(rowData.order_date) : null,
            planned_date_real: rowData.planned_date_real ? formatDateForBackend(rowData.planned_date_real) : null,
            shipment_date: rowData.shipment_date ? formatDateForBackend(rowData.shipment_date) : null,
            planned_date_mirror: rowData.planned_date_mirror ? formatDateForBackend(rowData.planned_date_mirror) : null,
            planned_dates: Array.isArray(rowData.planned_dates)
                ? rowData.planned_dates.map(date => formatDateForBackend(date)).filter(Boolean)
                : []
        };
    
        try {
            if (rowId === 'new') {
                await addShipmentOrder(updatedData);
                setNewRow(null);
            } else {
                await modifyShipmentOrder(rowId, updatedData);
            }
            await loadShipmentOrders();
        } catch (error) {
            console.error('Guncelleme sirasinda bir hata olustu:', error);
            alert(`Guncelleme sirasinda bir hata olustu: ${error.message}`);
        }
    };

    const handleAddNewRow = useCallback(() => {
        setNewRow({
            id: 'new',
            order_status: 'Acik',
            order_number: '',
            customer_name: '',
            order_date: null,
            shipment_date: null,
            planned_date_real: null,
            planned_date_week: selectedWeek,
            planned_date_mirror: null,
            sales_person: '',
            shipment_details: '',
            shipment_notes: '',
            planned_dates: []
        });
    }, [selectedWeek]);

    useEffect(() => {
        if (shouldAddNewRow) {
            handleAddNewRow();
            onNewRowAdded();
        }
    }, [shouldAddNewRow, onNewRowAdded, handleAddNewRow]);
    
    const handleRemoveNewRow = () => {
        if (window.confirm('Yeni eklenen satir silinecek. Devam etmek istiyor musunuz?')) {
            setNewRow(null);
        }
    };

    const parseDate = (dateString) => {
        if (!dateString) return null;
        const parsedDate = dayjs(dateString, 'YYYY-MM-DD', true);
        return parsedDate.isValid() ? parsedDate.toDate() : null;
    };

    // Renk secimi islevi
    const handleColorSelect = useCallback((orderId, color) => {
        // 'editableData' icindeki ilgili siparisin rengini guncelle
        setEditableData((prevData) => ({
            ...prevData,
            [orderId]: { ...prevData[orderId], selected_color: color }
        }));
        // Backend'e kaydet
        saveSelectedColor(orderId, color);
    }, [saveSelectedColor]);

    // Hucre render fonksiyonu
    const renderCell = (rowId, column, dayOfWeek, rowData) => {
        const isNewRow = rowId === 'new';
        const cellData = isNewRow ? newRow : editableData[rowId];
        const cellStyle = { ...columnStyles[column.accessor] };
        const isNonEditable = !column.editable;

        // Belirli hucreler icin arka plan rengini ayarla
        if (['customer_name', 'shipment_details'].includes(column.accessor)) {
            cellStyle.backgroundColor = rowData.selected_color || 'transparent';
            cellStyle.color = '#000000'; // Metin rengini siyah yap
        }

        if (column.accessor === 'day_of_week') {
            return (
                <td key={`${rowId}-${column.accessor}`} style={cellStyle}>
                    <div style={{ display: 'flex', alignItems: 'center' }}>
                        <PaintThePlan
                            currentColor={rowData.selected_color || '#fff'}
                            onColorSelect={(color) => handleColorSelect(rowId, color)}
                        />
                        <span>{dayOfWeek}</span>
                    </div>
                </td>
            );
        }

        // SevkAdres ve SevkNotlari icin ozel gorunum
        if (column.accessor === 'shipment_details' || column.accessor === 'shipment_notes') {
            return (
                <td key={`${rowId}-${column.accessor}`} style={cellStyle}>
                    <ExpandableCell
                        value={cellData?.[column.accessor] || ''}
                        onChange={(e) => handleCellChange(rowId, column.accessor, e.target.value)}
                        disabled={isNonEditable}
                    />
                </td>
            );
        }

        // Tarih alanlari icin gorunum
        if (column.isDate) {
            return (
                <td 
                    key={`${rowId}-${column.accessor}`} 
                    style={cellStyle}
                    className={isNonEditable ? 'non-editable' : ''}
                >
                    <div className="datepicker-root">
                        <DatePicker
                            selected={cellData?.[column.accessor]}
                            onChange={(date) => handleCellChange(rowId, column.accessor, date)}
                            dateFormat="dd.MM.yyyy"
                            isClearable={!isNonEditable}
                            placeholderText="Tarih secin"
                            disabled={isNonEditable}
                            locale="tr"
                            className={isNonEditable ? 'non-editable' : ''}
                            popperProps={{
                                positionFixed: true
                            }}
                            popperModifiers={{
                                preventOverflow: {
                                    enabled: true,
                                    escapeWithReference: false,
                                    boundariesElement: 'viewport'
                                }
                            }}
                            popperPlacement="bottom-start"
                            showYearDropdown
                            showMonthDropdown
                            dropdownMode="select"
                            todayButton="Bugun"
                            customInput={
                                <input
                                    style={{
                                        width: '100%',
                                        height: '100%',
                                        padding: '0 4px',
                                        border: 'none',
                                        fontSize: '0.875rem',
                                        backgroundColor: !column.editable ? 'var(--swp-non-editable-bg)' : 'transparent',
                                        color: !column.editable ? 'var(--swp-non-editable-text)' : 'inherit',
                                        cursor: !column.editable ? 'not-allowed' : 'pointer',
                                        textAlign: column.accessor === 'planned_date_real' ? 'center' : 'left',
                                        overflow: 'hidden',
                                        textOverflow: 'ellipsis',
                                        whiteSpace: 'nowrap'
                                    }}
                                />
                            }
                        />
                    </div>
                </td>
            );
        }

        // Diger hucreler icin standart gorunum
        return (
            <td 
                key={`${rowId}-${column.accessor}`} 
                style={cellStyle}
                className={!column.editable ? 'non-editable' : ''}
            >
                {column.isDate ? (
                    <div className="datepicker-root">
                        <DatePicker
                            selected={cellData?.[column.accessor]}
                            onChange={(date) => handleCellChange(rowId, column.accessor, date)}
                            dateFormat="dd.MM.yyyy"
                            isClearable={column.editable}
                            placeholderText="Tarih secin"
                            disabled={!column.editable}
                            locale="tr"
                            className={!column.editable ? 'non-editable' : ''}
                            popperProps={{
                                positionFixed: true
                            }}
                            popperModifiers={{
                                preventOverflow: {
                                    enabled: true,
                                    escapeWithReference: false,
                                    boundariesElement: 'viewport'
                                }
                            }}
                            popperPlacement="bottom-start"
                            showYearDropdown
                            showMonthDropdown
                            dropdownMode="select"
                            todayButton="Bugun"
                        />
                    </div>
                ) : (
                    <TextField
                        value={cellData?.[column.accessor] || ''}
                        onChange={(e) => handleCellChange(rowId, column.accessor, e.target.value)}
                        fullWidth
                        size="small"
                        variant="standard"
                        disabled={!column.editable}
                        InputProps={{
                            disableUnderline: true,
                            readOnly: !column.editable,
                            style: {
                                padding: '4px 8px',
                                fontSize: '0.875rem',
                                backgroundColor: !column.editable ? 'var(--swp-non-editable-bg)' : 'transparent',
                                color: !column.editable ? 'var(--swp-non-editable-text)' : 'inherit',
                                cursor: !column.editable ? 'not-allowed' : 'text'
                            }
                        }}
                    />
                )}
            </td>
        );
    };

    if (loading) return <Typography>Yukleniyor...</Typography>;
    if (error) return <Typography color="error">{error}</Typography>;

    return (
        <div className="ShipWeekPlanner__tableContainer">
            <table className="ShipWeekPlanner__table ShipWeekPlanner__table--editable">
                <thead>
                    <tr>
                        {columns.map((column) => (
                            <th key={column.accessor} style={columnStyles[column.accessor]}>
                                {column.Header}
                            </th>
                        ))}
                        <th style={{ width: '100px', minWidth: '100px' }}>0slemler</th>
                    </tr>
                </thead>
                <tbody>
                    {newRow && (
                        <tr>
                            {columns.map((column) => renderCell('new', column, '', newRow))}
                            <td style={{ width: '100px', minWidth: '100px' }}>
                                <div style={{ display: 'flex', alignItems: 'center' }}>
                                    <Button
                                        variant="contained"
                                        color="primary"
                                        onClick={() => handleSaveRow('new')}
                                        size="small"
                                        className="ShipWeekPlanner__addRow"
                                    >
                                        Kaydet
                                    </Button>
                                    <button
                                        type="button"
                                        className="ShipWeekPlanner__deleteButton"
                                        onClick={handleRemoveNewRow}
                                    >
                                        Sil
                                    </button>
                                </div>
                            </td>
                        </tr>
                    )}
                    {getFilteredData().length > 0
                        ? Object.entries(groupByDayOfWeek(getFilteredData())).flatMap(([dayName, orders]) =>
                            orders.map((order) => (
                                <tr key={order.id}>
                                    {columns.map((column) => renderCell(order.id, column, dayName, order))}
                                
                                    <td style={{ width: '150px', minWidth: '150px' }}>
                                        <div style={{ display: 'flex', alignItems: 'center' }}>
                                            <Button
                                                variant="contained"
                                                color="primary"
                                                onClick={() => handleSaveRow(order.id)}
                                                size="small"
                                                className="ShipWeekPlanner__addRow"
                                            >
                                                Kaydet
                                            </Button>
                                            <CopyToForm 
                                                rowData={order} 
                                                onCopy={handleCopyRow}
                                            />
                                        </div>
                                    </td>
                                </tr>
                            ))
                        )
                        : (
                            <tr>
                                <td colSpan={columns.length + 1} style={{ textAlign: 'center', padding: '20px' }}>
                                    Bu filtre icin gosterilecek veri yok.
                                </td>
                            </tr>
                        )}
                </tbody>
            </table>
        </div>
    );
};

export default WeekTable;