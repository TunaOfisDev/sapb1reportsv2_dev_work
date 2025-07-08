// frontend/src/components/ShipWeekPlanner/utils/weekSelectCalender.js
import React, { useState, useEffect, useCallback } from 'react';
import { 
    Button, 
    Dialog, 
    DialogTitle, 
    DialogContent, 
    IconButton,
    Grid,
    Typography,
    Select,
    MenuItem
} from '@mui/material';
import CloseIcon from '@mui/icons-material/Close';
import CalendarTodayIcon from '@mui/icons-material/CalendarToday';
import NavigateBeforeIcon from '@mui/icons-material/NavigateBefore';
import NavigateNextIcon from '@mui/icons-material/NavigateNext';
import { getWeekNumber, getWeekRange } from './dateToWeek';
import useShipWeekPlanner from '../hooks/useShipWeekPlanner';
import '../css/weekSelectCalender.css';

const WeekSelectCalendar = ({ selectedWeek, onWeekSelect }) => {
    const [open, setOpen] = useState(false);
    const [selectedYear, setSelectedYear] = useState(new Date().getFullYear());
    const [weeks, setWeeks] = useState([]);
    const { weekCounts } = useShipWeekPlanner();

    const generateWeeks = useCallback(() => {
        const weeksInYear = [];
        const startDate = new Date(selectedYear, 0, 1);
        const endDate = new Date(selectedYear, 11, 31);
        const currentDate = new Date(startDate);

        // Yılın ilk haftasının başlangıcına git
        while (currentDate.getDay() !== 1) {
            currentDate.setDate(currentDate.getDate() - 1);
        }

        // Haftaları yatay sırayla oluştur
        while (currentDate <= endDate) {
            const weekNumber = getWeekNumber(currentDate);
            const { weekStart, weekEnd } = getWeekRange(new Date(currentDate));
            const recordCount = weekCounts[weekNumber] || 0;

            weeksInYear.push({
                weekNumber,
                startDate: new Date(weekStart).toLocaleDateString('tr-TR', { day: '2-digit', month: '2-digit' }),
                endDate: new Date(weekEnd).toLocaleDateString('tr-TR', { day: '2-digit', month: '2-digit' }),
                belongs: new Date(currentDate).getFullYear() === selectedYear,
                recordCount
            });

            currentDate.setDate(currentDate.getDate() + 7);
        }

        // 13'er haftalık satırlar oluştur (soldan sağa)
        const rows = Math.ceil(weeksInYear.length / 13);
        const gridWeeks = Array.from({ length: rows }, (_, row) => 
            weeksInYear.slice(row * 13, (row + 1) * 13)
        );

        setWeeks(gridWeeks);
    }, [selectedYear, weekCounts]);

    useEffect(() => {
        generateWeeks();
    }, [generateWeeks]);

    const years = Array.from(
        { length: 5 },
        (_, i) => selectedYear - 2 + i
    );

    const handleYearChange = (event) => {
        setSelectedYear(event.target.value);
    };

    const handleWeekSelect = (weekNumber) => {
        onWeekSelect(weekNumber);
        setOpen(false);
    };

    const handlePrevYear = () => {
        setSelectedYear(prev => prev - 1);
    };

    const handleNextYear = () => {
        setSelectedYear(prev => prev + 1);
    };

    return (
        <>
            <Button
                variant="outlined"
                startIcon={<CalendarTodayIcon />}
                onClick={() => setOpen(true)}
                className="week-select-button"
            >
                {selectedWeek ? `${selectedYear} - ${selectedWeek}. Hafta` : 'Hafta Seç'}
            </Button>

            <Dialog
                open={open}
                onClose={() => setOpen(false)}
                maxWidth="lg"
                fullWidth
                className="week-select-dialog"
            >
                <DialogTitle className="week-select-dialog__title">
                    <div className="week-select-dialog__header">
                        <IconButton onClick={handlePrevYear}>
                            <NavigateBeforeIcon />
                        </IconButton>
                        <Select
                            value={selectedYear}
                            onChange={handleYearChange}
                            variant="standard"
                            className="year-select"
                        >
                            {years.map(year => (
                                <MenuItem key={year} value={year}>{year}</MenuItem>
                            ))}
                        </Select>
                        <IconButton onClick={handleNextYear}>
                            <NavigateNextIcon />
                        </IconButton>
                    </div>
                    <IconButton
                        onClick={() => setOpen(false)}
                        className="close-button"
                    >
                        <CloseIcon />
                    </IconButton>
                </DialogTitle>

                <DialogContent className="week-select-dialog__content">
                    {weeks.map((row, rowIndex) => (
                        <Grid container spacing={1} key={rowIndex} className="week-row">
                            {row.map((week) => (
                                <Grid item xs key={week.weekNumber}>
                                    <Button
                                        onClick={() => handleWeekSelect(week.weekNumber)}
                                        className={`week-button ${selectedWeek === week.weekNumber ? 'selected' : ''} ${!week.belongs ? 'other-year' : ''}`}
                                        fullWidth
                                        disabled={!week.belongs}
                                    >
                                        <Typography variant="body2" className="week-number">
                                            {week.weekNumber}
                                        </Typography>
                                        <Typography variant="caption" className="week-dates">
                                            {week.startDate} - {week.endDate}
                                        </Typography>
                                        {week.belongs && (
                                            <Typography variant="caption" className="week-count">
                                                {week.recordCount} kayıt
                                            </Typography>
                                        )}
                                    </Button>
                                </Grid>
                            ))}
                        </Grid>
                    ))}
                </DialogContent>
            </Dialog>
        </>
    );
};

export default WeekSelectCalendar;