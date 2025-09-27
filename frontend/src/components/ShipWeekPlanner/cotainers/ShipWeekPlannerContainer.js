// frontend/src/components/ShipWeekPlanner/containers/ShipWeekPlannerContainer.js
import React, { useState, useEffect } from 'react';
import WeekCalendar from '../views/WeekCalendar';
import WeekTable from './WeekTable';
import GeneralSearch from '../components/GeneralSearch'; // GeneralSearch bileşenini import edin
import useShipWeekPlanner from '../hooks/useShipWeekPlanner';
import { Grid, Typography, Button } from '@mui/material';
import { handleExportPDF, handleExportXLSX } from '../utils/pdfXlsxExport';
import WeekSelectCalendar from '../utils/weekSelectCalender';
import { dateToWeek } from '../utils/dateToWeek';
import '../css/ShipWeekPlanner.css';

const ShipWeekPlannerContainer = () => {
    const [selectedWeek, setSelectedWeek] = useState(null);
    const [shouldAddNewRow, setShouldAddNewRow] = useState(false);
    const [tableData, setTableData] = useState([]);
    const [filterStatus, setFilterStatus] = useState('Hepsi');

    // useShipWeekPlanner hook'unu tek bir yerde kullanın
    const { 
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
        searchOrders,
    } = useShipWeekPlanner(selectedWeek);

    // İlk yüklemede geçerli haftayı ayarla
    useEffect(() => {
        const currentDate = new Date();
        const { weekNumber } = dateToWeek(currentDate);
        setSelectedWeek(weekNumber);
    }, []);

    const handleWeekSelect = (week) => {
        setSelectedWeek(week);
    };

    const handleAddNewRow = () => {
        setShouldAddNewRow(true);
    };

    // WeekTable'dan gelen veriyi günceller
    const handleTableDataChange = (data) => {
        setTableData(data);
    };

    // Filtreleme butonları için handle fonksiyonu
    const handleFilterChange = (status) => {
        setFilterStatus(status);
    };

    // Arama fonksiyonu
    const handleSearch = (query) => {
        searchOrders(query);
    };

    return (
        <div className="ShipWeekPlanner">
            <Typography 
                variant="h4" 
                className="ShipWeekPlanner__header"
                sx={{ 
                    fontWeight: 500,
                    '& .week-number': {
                        color: 'primary.main',
                        fontWeight: 600
                    }
                }}
            >
                {selectedWeek ? (
                    <>
                        {'Haftalık Sevk Planlama '}
                        <span className="week-number">{selectedWeek}. Hafta</span>
                    </>
                ) : (
                    'Haftalık Sevk Planlama'
                )}
            </Typography>
            <Grid container spacing={2} alignItems="center" className="ShipWeekPlanner__controls">
                <Grid item xs={12} md={6}>
                    <WeekCalendar onWeekSelect={handleWeekSelect} />
                </Grid>
                <Grid item xs={12} md={2}>
                    <WeekSelectCalendar 
                        selectedWeek={selectedWeek}
                        onWeekSelect={handleWeekSelect}
                    />
                </Grid>
                <Grid item xs={12} md={4}>
                    <Button 
                        variant="contained" 
                        color="primary" 
                        fullWidth
                        onClick={handleAddNewRow}
                        disabled={!selectedWeek}
                    >
                        YENİ SEVK PLANI EKLE
                    </Button>
                </Grid>
            </Grid>

            {selectedWeek ? (
                <>
                    {/* Filtreleme, Arama ve Export Butonları Aynı Satırda */}
                    <Grid container spacing={2} className="ShipWeekPlanner__buttons" alignItems="center">
                        <Grid item xs={12}>
                            <Grid container spacing={2} justifyContent="space-between">
                                {/* Filtreleme Butonları */}
                                <Grid item>
                                    <Button
                                        variant={filterStatus === 'Acik' ? 'contained' : 'outlined'}
                                        color="primary"
                                        onClick={() => handleFilterChange('Acik')}
                                    >
                                        Acik
                                    </Button>
                                    <Button
                                        variant={filterStatus === 'Kapali' ? 'contained' : 'outlined'}
                                        color="primary"
                                        onClick={() => handleFilterChange('Kapali')}
                                        style={{ marginLeft: '10px' }}
                                    >
                                        Kapali
                                    </Button>
                                    <Button
                                        variant={filterStatus === 'Hepsi' ? 'contained' : 'outlined'}
                                        color="primary"
                                        onClick={() => handleFilterChange('Hepsi')}
                                        style={{ marginLeft: '10px' }}
                                    >
                                        Hepsi
                                    </Button>
                                </Grid>

                                {/* Genel Arama Butonu */}
                                <Grid item style={{ marginLeft: '20px' }}>
                                    <GeneralSearch onSearch={handleSearch} />
                                </Grid>

                                {/* Export Butonları */}
                                <Grid item>
                                    <Button
                                        variant="contained"
                                        color="secondary"
                                        onClick={() => handleExportPDF({ week: selectedWeek, orders: tableData })}
                                        disabled={tableData.length === 0} // Veriler yoksa buton devre dışı
                                    >
                                        PDF Olarak İndir
                                    </Button>
                                    <Button
                                        variant="contained"
                                        color="primary"
                                        onClick={() => handleExportXLSX({ week: selectedWeek, orders: tableData })}
                                        disabled={tableData.length === 0} // Veriler yoksa buton devre dışı
                                        style={{ marginLeft: '10px' }}
                                    >
                                        Excel Olarak İndir
                                    </Button>
                                </Grid>
                            </Grid>
                        </Grid>
                    </Grid>

                    {/* Haftalık Sevk Planı Tablosu */}
                    <WeekTable 
                        orders={filteredOrders}
                        loading={loading}
                        error={error}
                        addShipmentOrder={addShipmentOrder}
                        modifyShipmentOrder={modifyShipmentOrder}
                        removeShipmentOrder={removeShipmentOrder}
                        saveSelectedColor={saveSelectedColor}
                        loadShipmentOrders={loadShipmentOrders}
                        formatDateForBackend={formatDateForBackend}
                        formatDateForFrontend={formatDateForFrontend}
                        weekCounts={weekCounts}
                        selectedWeek={selectedWeek}
                        shouldAddNewRow={shouldAddNewRow}
                        onNewRowAdded={() => setShouldAddNewRow(false)}
                        onDataChange={handleTableDataChange}
                        filterStatus={filterStatus}
                    />
                </>
            ) : (
                <Typography className="ShipWeekPlanner__placeholder">
                    Lütfen bir hafta seçin
                </Typography>
            )}
        </div>
    );
};

export default ShipWeekPlannerContainer;
