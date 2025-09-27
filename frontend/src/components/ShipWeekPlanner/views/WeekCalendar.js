// frontend\src\components\ShipWeekPlanner\views\WeekCalendar.js
import React, { useState, useEffect } from 'react';
import { getCurrentWeek, getWeekRange, formatDate } from '../utils/dateUtils';
import { Button, Typography, Grid } from '@mui/material';

const getWeekNumber = (date) => {
    const firstDayOfYear = new Date(date.getFullYear(), 0, 1);
    const pastDaysOfYear = (date - firstDayOfYear + (firstDayOfYear.getTimezoneOffset() - date.getTimezoneOffset()) * 60000) / 86400000;
    return Math.ceil((pastDaysOfYear + firstDayOfYear.getDay() + 1) / 7);
};

const WeekCalendar = ({ onWeekSelect }) => {
    const [currentWeek, setCurrentWeek] = useState(getCurrentWeek());
    const [weekNumber, setWeekNumber] = useState(getWeekNumber(new Date(currentWeek.weekStart)));

    useEffect(() => {
        setWeekNumber(getWeekNumber(new Date(currentWeek.weekStart)));
    }, [currentWeek]);

    const handleNextWeek = () => {
        const nextWeek = new Date(currentWeek.weekStart);
        nextWeek.setDate(nextWeek.getDate() + 7);
        const nextWeekRange = getWeekRange(nextWeek.getFullYear(), getWeekNumber(nextWeek));
        setCurrentWeek({
            weekStart: formatDate(nextWeekRange.weekStartDate, 'DD.MM.YYYY'),
            weekEnd: formatDate(nextWeekRange.weekEndDate, 'DD.MM.YYYY'),
        });
        setWeekNumber(getWeekNumber(nextWeek));
    };

    const handlePreviousWeek = () => {
        const previousWeek = new Date(currentWeek.weekStart);
        previousWeek.setDate(previousWeek.getDate() - 7);
        const previousWeekRange = getWeekRange(previousWeek.getFullYear(), getWeekNumber(previousWeek));
        setCurrentWeek({
            weekStart: formatDate(previousWeekRange.weekStartDate, 'DD.MM.YYYY'),
            weekEnd: formatDate(previousWeekRange.weekEndDate, 'DD.MM.YYYY'),
        });
        setWeekNumber(getWeekNumber(previousWeek));
    };

    const handleWeekSelect = () => {
        if (onWeekSelect) {
            onWeekSelect(weekNumber);
        }
    };

    return (
        <Grid container spacing={1} alignItems="center">
            <Grid item>
                <Button variant="outlined" size="small" onClick={handlePreviousWeek}>
                    &lt;
                </Button>
            </Grid>
            <Grid item>
                <Typography variant="body1">
                    {currentWeek.weekStart} - {currentWeek.weekEnd} (Hafta {weekNumber})
                </Typography>
            </Grid>
            <Grid item>
                <Button variant="outlined" size="small" onClick={handleNextWeek}>
                    &gt;
                </Button>
            </Grid>
            <Grid item>
                <Button variant="contained" size="small" color="primary" onClick={handleWeekSelect}>
                    Seç
                </Button>
            </Grid>
        </Grid>
    );
};

export default WeekCalendar;