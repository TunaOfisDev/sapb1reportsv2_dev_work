// frontend/src/components/ShipWeekPlanner/utils/dateToWeek.js

// Verilen bir tarihi yılın hangi haftasına ait olduğunu hesaplar
export const getWeekNumber = (date) => {
    const d = new Date(Date.UTC(date.getFullYear(), date.getMonth(), date.getDate()));
    const dayNum = d.getUTCDay() || 7; // Pazartesi = 1, Pazar = 7
    d.setUTCDate(d.getUTCDate() + 4 - dayNum); // Haftanın ortasına getir
    const yearStart = new Date(Date.UTC(d.getUTCFullYear(), 0, 1));
    const weekNo = Math.ceil(((d - yearStart) / 86400000 + 1) / 7);
    return weekNo;
};

// Verilen bir tarihin bulunduğu haftanın başlangıç ve bitiş tarihlerini döndürür
export const getWeekRange = (date) => {
    const firstDayOfWeek = new Date(date.setDate(date.getDate() - date.getDay() + 1)); // Haftanın başlangıcı (Pazartesi)
    const lastDayOfWeek = new Date(firstDayOfWeek);
    lastDayOfWeek.setDate(firstDayOfWeek.getDate() + 6); // Haftanın sonu (Pazar)

    return {
        weekStart: firstDayOfWeek,
        weekEnd: lastDayOfWeek,
    };
};

// Tarihi formatlayıp "YYYY-MM-DD" olarak döndürür
export const formatDate = (date) => {
    const d = new Date(date);
    const year = d.getFullYear();
    const month = (`0${d.getMonth() + 1}`).slice(-2); // Ay iki haneli
    const day = (`0${d.getDate()}`).slice(-2); // Gün iki haneli
    return `${year}-${month}-${day}`;
};

// Verilen bir tarih için yılın hafta numarasını ve o haftanın başlangıç ve bitiş tarihlerini döndürür
export const dateToWeek = (date) => {
    const weekNumber = getWeekNumber(date);
    const { weekStart, weekEnd } = getWeekRange(new Date(date));

    return {
        weekNumber,
        weekStart: formatDate(weekStart),
        weekEnd: formatDate(weekEnd),
    };
};