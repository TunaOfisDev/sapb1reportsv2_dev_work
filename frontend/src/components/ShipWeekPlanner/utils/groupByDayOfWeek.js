// frontend\src\components\ShipWeekPlanner\utils\groupByDayOfWeek.js
import dayjs from 'dayjs';

// Haftanın günlerini istenen sırayla Türkçe olarak belirtelim
const daysOfWeek = ['Pazartesi', 'Salı', 'Çarşamba', 'Perşembe', 'Cuma', 'Cumartesi', 'Pazar'];

/**
 * Orders listesini haftanın günlerine göre gruplar.
 * @param {Array} orders - Sevk planlarının listesi.
 * @returns {Object} Günlere göre gruplanmış ve sıralanmış sevk planları.
 */
const groupByDayOfWeek = (orders) => {
    const groupedOrders = daysOfWeek.reduce((acc, day) => {
        acc[day] = [];
        return acc;
    }, {});

    orders.forEach(order => {
        const dayOfWeek = dayjs(order.planned_date_real).day(); // 0: Pazar, 1: Pazartesi...
        const dayName = daysOfWeek[(dayOfWeek + 6) % 7]; // Pazartesi'den başlayacak şekilde ayarlıyoruz
        groupedOrders[dayName].push(order);
    });

    // Boş günleri filtrele
    const filteredOrders = Object.entries(groupedOrders).filter(([_, orders]) => orders.length > 0);

    // Sıralı ve filtrelenmiş sonucu döndür
    return Object.fromEntries(filteredOrders);
};

export default groupByDayOfWeek;