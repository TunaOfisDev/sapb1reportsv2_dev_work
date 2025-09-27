// src/api/shipweekplanner.js
import axiosInstance from './axiosconfig';

// Tüm shipment order verilerini al (GET)
export const fetchShipmentOrders = async () => {
    try {
        const response = await axiosInstance.get('shipweekplanner/shipmentorders/');
        return response.data;
    } catch (error) {
        console.error("Error fetching shipment orders:", error);
        throw error;
    }
};


// Yeni bir shipment order oluştur (POST)
export const createShipmentOrder = async (orderData) => {
    try {
        const response = await axiosInstance.post('shipweekplanner/shipmentorders/', orderData);
        return response.data;
    } catch (error) {
        console.error("Error creating shipment order:", error);
        throw error;
    }
};

// Bir shipment order güncelle (PUT)
export const updateShipmentOrder = async (orderId, updatedData) => {
    try {
        const response = await axiosInstance.put(`shipweekplanner/shipmentorders/${orderId}/`, updatedData);
        console.log('Update response:', response);  // Yanıtı loglayalım
        if (response.status === 200) {
            return response.data;
        } else {
            throw new Error(`Unexpected response status: ${response.status}`);
        }
    } catch (error) {
        console.error(`Error updating shipment order with ID: ${orderId}`, error);
        if (error.response) {
            console.error('Error response:', error.response.data);
            throw new Error(JSON.stringify(error.response.data));
        }
        throw error;
    }
};

// Bir shipment order sil (DELETE)
export const deleteShipmentOrder = async (orderId) => {
    try {
        const response = await axiosInstance.delete(`shipmentorders/${orderId}/`);
        return response.data;
    } catch (error) {
        console.error(`Error deleting shipment order with ID: ${orderId}`, error);
        throw error;
    }
};