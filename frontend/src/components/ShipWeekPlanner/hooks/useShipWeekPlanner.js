// frontend/src/components/ShipWeekPlanner/hooks/useShipWeekPlanner.js
import { useState, useEffect, useCallback } from 'react';
import {
    fetchShipmentOrders,
    createShipmentOrder,
    updateShipmentOrder,
    deleteShipmentOrder
} from '../../../api/shipweekplanner';
import dayjs from 'dayjs';

const useShipWeekPlanner = (selectedWeek) => {
    const [orders, setOrders] = useState([]);
    const [filteredOrders, setFilteredOrders] = useState([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const [weekCounts, setWeekCounts] = useState({});

    const formatDateForBackend = (date) => {
        if (!date) return null;
        return dayjs(date).format('YYYY-MM-DD');
    };

    const formatDateForFrontend = (date) => {
        if (!date) return null;
        return dayjs(date).format('DD.MM.YYYY');
    };

    const loadShipmentOrders = useCallback(async () => {  
        setLoading(true);
        setError(null);
        try {
            const data = await fetchShipmentOrders();
            setOrders(data);
        } catch (err) {
            setError('Error fetching shipment orders');
            console.error(err);
        } finally {
            setLoading(false);
        }
    }, []);

    useEffect(() => {
        if (selectedWeek) {
            const filtered = orders.filter(order => order.planned_date_week === selectedWeek);
            setFilteredOrders(filtered);
        } else {
            setFilteredOrders(orders);
        }
    }, [orders, selectedWeek]);

    const addShipmentOrder = async (orderData) => {
        setLoading(true);
        setError(null);
        try {
            const formattedOrderData = {
                ...orderData,
                order_date: formatDateForBackend(orderData.order_date),
                planned_date_real: formatDateForBackend(orderData.planned_date_real),
                shipment_date: formatDateForBackend(orderData.shipment_date),
                planned_date_mirror: formatDateForBackend(orderData.planned_date_mirror),
                planned_dates: orderData.planned_dates.map(formatDateForBackend)
            };
            const newOrder = await createShipmentOrder(formattedOrderData);
            setOrders((prevOrders) => [...prevOrders, newOrder]);
        } catch (err) {
            setError('Error creating shipment order');
            console.error(err);
            throw err;
        } finally {
            setLoading(false);
        }
    };
    
    const modifyShipmentOrder = async (orderId, updatedData) => {
        setLoading(true);
        setError(null);
        try {
            const formattedUpdatedData = {
                ...updatedData,
                order_date: formatDateForBackend(updatedData.order_date),
                planned_date_real: formatDateForBackend(updatedData.planned_date_real),
                shipment_date: formatDateForBackend(updatedData.shipment_date),
                planned_date_mirror: formatDateForBackend(updatedData.planned_date_mirror),
                planned_dates: Array.isArray(updatedData.planned_dates)
                    ? updatedData.planned_dates.map(formatDateForBackend).filter(Boolean)
                    : []
            };
            const updatedOrder = await updateShipmentOrder(orderId, formattedUpdatedData);
            setOrders((prevOrders) =>
                prevOrders.map((order) =>
                    order.id === orderId ? { ...order, ...updatedOrder } : order
                )
            );
            return updatedOrder;
        } catch (err) {
            const errorMessage = err.response?.data?.detail || err.message || 'Bilinmeyen bir hata oluştu';
            setError(`Sevkiyat siparişi güncellenirken hata oluştu (ID: ${orderId}): ${errorMessage}`);
            console.error(err);
            throw err;
        } finally {
            setLoading(false);
        }
    };

    const removeShipmentOrder = async (orderId) => {
        setLoading(true);
        setError(null);
        try {
            await deleteShipmentOrder(orderId);
            setOrders((prevOrders) =>
                prevOrders.filter((order) => order.id !== orderId)
            );
        } catch (err) {
            setError(`Error deleting shipment order with ID: ${orderId}`);
            console.error(err);
            throw err;
        } finally {
            setLoading(false);
        }
    };

    const saveSelectedColor = async (orderId, color) => {
        // Önce UI'yi hemen güncelle
        setOrders((prevOrders) =>
            prevOrders.map((order) =>
                order.id === orderId ? { ...order, selected_color: color } : order
            )
        );
    
        // Backend'e kaydet
        try {
            await updateShipmentOrder(orderId, { selected_color: color });
        } catch (err) {
            setError('Error updating selected color');
            console.error(err);
        }
    };
    
    // Arama Fonksiyonu
    const searchOrders = (query) => {
        if (!query) {
            setFilteredOrders(orders);
        } else {
            const lowerCaseQuery = query.toLowerCase();
            setFilteredOrders(
                orders.filter(order => 
                    order.order_number?.toString().includes(lowerCaseQuery) ||
                    order.customer_name?.toLowerCase().includes(lowerCaseQuery) ||
                    order.shipment_details?.toLowerCase().includes(lowerCaseQuery)
                )
            );
        }
    };

    useEffect(() => {
        loadShipmentOrders();
    }, [loadShipmentOrders]);

    useEffect(() => {
        const calculateWeekCounts = () => {
            const counts = filteredOrders.reduce((acc, order) => {
                const week = order.planned_date_week;
                acc[week] = (acc[week] || 0) + 1;
                return acc;
            }, {});
            setWeekCounts(counts);
        };

        calculateWeekCounts();
    }, [filteredOrders]);

    return {
        filteredOrders,
        loading,
        error,
        addShipmentOrder,
        modifyShipmentOrder,
        removeShipmentOrder,
        saveSelectedColor,
        loadShipmentOrders,
        formatDateForBackend,
        formatDateForFrontend,
        weekCounts,
        searchOrders, // Arama fonksiyonunu geri ekleyin
    };
};

export default useShipWeekPlanner;
