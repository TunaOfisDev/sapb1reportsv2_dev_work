// frontend\src\components\ShipWeekPlanner\views\WeekDetails.js
import React, { useState, useMemo } from 'react';
import { useTable } from 'react-table';
import { Button, TextField, Typography } from '@mui/material';
import useShipWeekPlanner from '../hooks/useShipWeekPlanner';
import '../css/ShipWeekPlanner.css';
import { formatDateForFrontend, formatDateForBackend } from '../utils/dateUtils';

const WeekDetails = ({ selectedWeek }) => {
    const { filteredOrders, loading, error, addShipmentOrder, modifyShipmentOrder } = useShipWeekPlanner(selectedWeek);
    const [newOrder, setNewOrder] = useState({
        order_number: '',
        customer_name: '',
        order_date: '',
        planned_dates: [],
        shipment_date: '',
        sales_person: '',
        shipment_details: '',
        shipment_notes: '',
        planned_date_real: ''
    });

    const handleInputChange = (e) => {
        const { name, value } = e.target;
        setNewOrder((prevState) => ({
            ...prevState,
            [name]: value,
        }));
    };

    const handleAddOrder = async () => {
        try {
            const orderToAdd = {
                ...newOrder,
                order_date: formatDateForBackend(newOrder.order_date),
                shipment_date: formatDateForBackend(newOrder.shipment_date),
                planned_date_real: formatDateForBackend(newOrder.planned_date_real),
                planned_dates: newOrder.planned_dates.map(formatDateForBackend)
            };
            await addShipmentOrder(orderToAdd);
            setNewOrder({
                order_number: '',
                customer_name: '',
                order_date: '',
                planned_dates: [],
                shipment_date: '',
                sales_person: '',
                shipment_details: '',
                shipment_notes: '',
                planned_date_real: ''
            });
        } catch (error) {
            console.error('Sevk planı eklenirken hata:', error);
        }
    };

    const handleUpdateOrder = async (rowId, rowData) => {
        try {
            const updatedData = {
                ...rowData,
                order_date: formatDateForBackend(rowData.order_date),
                shipment_date: formatDateForBackend(rowData.shipment_date),
                planned_date_real: formatDateForBackend(rowData.planned_date_real),
                planned_dates: rowData.planned_dates.map(formatDateForBackend)
            };
            await modifyShipmentOrder(rowId, updatedData);
        } catch (error) {
            console.error('Sevk planı güncellenirken hata:', error);
        }
    };

    const columns = useMemo(() => [
        { Header: 'SiparisNo', accessor: 'order_number' },
        { Header: 'MusteriAd', accessor: 'customer_name' },
        { Header: 'SiparisTarihi', accessor: 'order_date' },
        { Header: 'PlanlananTarihler', accessor: 'planned_dates', Cell: ({ value }) => value.map(formatDateForFrontend).join(', ') },
        { Header: 'SevkTarihi', accessor: 'shipment_date' },
        { Header: 'Satici', accessor: 'sales_person' },
        { Header: 'SevkAciklamalari', accessor: 'shipment_details' },
        { Header: 'SevkNotlari', accessor: 'shipment_notes' },
        { Header: 'GercekPlanlananTarih', accessor: 'planned_date_real' },
        { Header: 'PlanlananHafta', accessor: 'planned_date_week' }
    ], []);

    const data = useMemo(() => 
        filteredOrders.map(order => ({
            ...order,
            order_date: formatDateForFrontend(order.order_date),
            shipment_date: formatDateForFrontend(order.shipment_date),
            planned_date_real: formatDateForFrontend(order.planned_date_real)
        })) || [], 
    [filteredOrders]);

    const {
        getTableProps,
        getTableBodyProps,
        headerGroups,
        rows,
        prepareRow
    } = useTable({
        columns,
        data,
    });

    if (loading) {
        return <Typography>Yükleniyor...</Typography>;
    }

    if (error) {
        return <Typography color="error">{error}</Typography>;
    }

    return (
        <div>
            <Typography variant="h6">
                Seçilen Hafta: {formatDateForFrontend(selectedWeek)} için Sevk Planları
            </Typography>

            <table {...getTableProps()} className="ShipWeekPlanner__table">
                <thead>
                    {headerGroups.map(headerGroup => (
                        <tr {...headerGroup.getHeaderGroupProps()}>
                            {headerGroup.headers.map(column => (
                                <th {...column.getHeaderProps()}>{column.render('Header')}</th>
                            ))}
                        </tr>
                    ))}
                </thead>
                <tbody {...getTableBodyProps()}>
                    {rows.length > 0 ? (
                        rows.map(row => {
                            prepareRow(row);
                            return (
                                <tr {...row.getRowProps()}>
                                    {row.cells.map(cell => (
                                        <td {...cell.getCellProps()}>
                                            {cell.column.id === 'planned_dates' ? (
                                                cell.render('Cell')
                                            ) : (
                                                <TextField
                                                    defaultValue={cell.value}
                                                    onBlur={(e) =>
                                                        handleUpdateOrder(row.original.id, {
                                                            ...row.original,
                                                            [cell.column.id]: e.target.value
                                                        })
                                                    }
                                                />
                                            )}
                                        </td>
                                    ))}
                                </tr>
                            );
                        })
                    ) : (
                        <tr>
                            <td colSpan={columns.length}>Bu hafta için sevk planı yok.</td>
                        </tr>
                    )}
                </tbody>
            </table>

            <Typography variant="h6" style={{ marginTop: '20px' }}>
                Yeni Sevk Planı Ekle
            </Typography>
            <div className="ShipWeekPlanner__addRow">
                <TextField
                    name="order_number"
                    label="SiparisNo"
                    value={newOrder.order_number}
                    onChange={handleInputChange}
                />
                <TextField
                    name="customer_name"
                    label="MusteriAd"
                    value={newOrder.customer_name}
                    onChange={handleInputChange}
                />
                <TextField
                    name="order_date"
                    label="SiparisTarihi"
                    value={newOrder.order_date}
                    onChange={handleInputChange}
                />
                <TextField
                    name="planned_dates"
                    label="PlanlananTarihler"
                    value={newOrder.planned_dates.join(', ')}
                    onChange={(e) => handleInputChange({
                        target: {
                            name: 'planned_dates',
                            value: e.target.value.split(', ')
                        }
                    })}
                />
                <TextField
                    name="planned_date_real"
                    label="GercekPlanlananTarih"
                    value={newOrder.planned_date_real}
                    onChange={handleInputChange}
                />
                <TextField
                    name="shipment_date"
                    label="SevkTarihi"
                    value={newOrder.shipment_date}
                    onChange={handleInputChange}
                />
                <TextField
                    name="sales_person"
                    label="Satici"
                    value={newOrder.sales_person}
                    onChange={handleInputChange}
                />
                <TextField
                    name="shipment_details"
                    label="SevkAciklamalari"
                    value={newOrder.shipment_details}
                    onChange={handleInputChange}
                />
                <TextField
                    name="shipment_notes"
                    label="SevkNotlari"
                    value={newOrder.shipment_notes}
                    onChange={handleInputChange}
                />
            </div>

            <Button
                variant="contained"
                color="primary"
                onClick={handleAddOrder}
                style={{ marginTop: '20px' }}
            >
                Sevk Planı Ekle
            </Button>
        </div>
    );
};

export default WeekDetails;