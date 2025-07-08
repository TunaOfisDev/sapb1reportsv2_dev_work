// frontend\src\components\ShipWeekPlanner\utils\dateUtils.js
import dayjs from 'dayjs';
import customParseFormat from 'dayjs/plugin/customParseFormat';

dayjs.extend(customParseFormat);

// Türkiye standartlarına uygun tarih formatlama (DD.MM.YYYY)
export const formatDateForFrontend = (date) => {
    if (!date) return '';
    return dayjs(date).format('DD.MM.YYYY');
};


export const formatDateForBackend = (date) => {
    if (!date) return null;
    let parsedDate;
    if (date instanceof Date) {
        parsedDate = dayjs(date);
    } else {
        parsedDate = dayjs(date, ['DD.MM.YYYY', 'YYYY-MM-DD', 'YYYY-MM-DDTHH:mm:ss.SSSSZ'], true);
    }
    return parsedDate.isValid() ? parsedDate.format('YYYY-MM-DD') : null;
};

// Haftanın başlangıç ve bitiş tarihini hesaplar (ISO hafta standardı kullanılarak)
export const getWeekRange = (year, weekNumber) => {
    const firstDayOfYear = new Date(year, 0, 1);
    const days = (weekNumber - 1) * 7;
    const weekStart = new Date(firstDayOfYear.setDate(firstDayOfYear.getDate() + days));
    
    // Pazartesi başlangıç, Pazar bitiş olarak hesaplanır
    const weekStartDate = new Date(weekStart.setDate(weekStart.getDate() - weekStart.getDay() + 1));
    const weekEndDate = new Date(weekStartDate);
    weekEndDate.setDate(weekStartDate.getDate() + 6);

    return {
        weekStartDate,
        weekEndDate,
    };
};

// Tarihler arasındaki farkı gün cinsinden hesaplar
export const calculateDateDifference = (date1, date2) => {
    const oneDayInMilliseconds = 24 * 60 * 60 * 1000; // Bir günün milisaniye cinsinden değeri
    const diffInTime = new Date(date2) - new Date(date1);
    const diffInDays = Math.round(diffInTime / oneDayInMilliseconds);
    return diffInDays;
};

// Bir tarih aralığının içinde olup olmadığını kontrol eder
export const isDateInRange = (date, startDate, endDate) => {
    const targetDate = new Date(date);
    return targetDate >= new Date(startDate) && targetDate <= new Date(endDate);
};

// Tarihi "YYYY-MM-DD" formatında döner
export const formatDate = (date) => {
    const d = new Date(date);
    const year = d.getFullYear();
    const month = (`0${d.getMonth() + 1}`).slice(-2); // Ay iki haneli
    const day = (`0${d.getDate()}`).slice(-2); // Gün iki haneli
    return `${year}-${month}-${day}`;
};

// Geçerli haftanın başlangıç ve bitiş tarihini getirir
export const getCurrentWeek = () => {
    const today = new Date();
    const first = today.getDate() - today.getDay() + 1; // Pazartesi günü başlangıç
    const last = first + 6; // Pazar günü bitiş
    const weekStart = new Date(today.setDate(first));
    const weekEnd = new Date(today.setDate(last));

    return {
        weekStart: formatDate(weekStart),
        weekEnd: formatDate(weekEnd),
    };
};

// Tarihin geçerli olup olmadığını kontrol eder
export const isValidDate = (date) => {
    const parsedDate = new Date(date);
    return parsedDate instanceof Date && !isNaN(parsedDate);
};