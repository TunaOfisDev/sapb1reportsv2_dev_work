// frontend/src/components/ShipWeekPlanner/utils/paintThePlan.js
import React, { useState } from 'react';
import { IconButton, Box, Popover, Button, Tooltip } from '@mui/material';
import ColorLensIcon from '@mui/icons-material/ColorLens';
import FormatColorResetIcon from '@mui/icons-material/FormatColorReset';
import '../css/paintThePlan.css';

const colorSchemes = [
    { color: "#4dabf5", label: "Mavi", textColor: "#000000" },     // Orta ton mavi
    { color: "#66bb6a", label: "Yeşil", textColor: "#000000" },    // Orta ton yeşil
    { color: "#ffd54f", label: "Sarı", textColor: "#000000" },     // Orta ton sarı
    { color: "#ef5350", label: "Kırmızı", textColor: "#000000" },  // Orta ton kırmızı
    { color: null, label: "Renksiz", textColor: "#000000" }        // Renksiz seçenek
];

const PaintThePlan = ({ currentColor, onColorSelect }) => {
    const [anchorEl, setAnchorEl] = useState(null);

    const handleClick = (event) => {
        setAnchorEl(event.currentTarget);
    };

    const handleClose = () => {
        setAnchorEl(null);
    };

    const handleColorSelect = (colorScheme) => {
        // Backend'e sadece renk değerini gönder
        onColorSelect(colorScheme.color); 
        handleClose();
    };


    const open = Boolean(anchorEl);

    return (
        <Box className="paintThePlan">
            <Tooltip title="Renk Seç">
                <IconButton
                    onClick={handleClick}
                    className="paintThePlan__icon"
                    size="small"
                >
                    <ColorLensIcon
                        style={{
                            color: currentColor || '#757575',
                            fontSize: '1.2rem'
                        }}
                    />
                </IconButton>
            </Tooltip>
            <Popover
                open={open}
                anchorEl={anchorEl}
                onClose={handleClose}
                anchorOrigin={{
                    vertical: 'bottom',
                    horizontal: 'left',
                }}
                transformOrigin={{
                    vertical: 'top',
                    horizontal: 'left',
                }}
                className="paintThePlan__popover"
            >
                <Box className="paintThePlan__palette">
                    {colorSchemes.map((scheme) => (
                        <Tooltip key={scheme.label} title={scheme.label}>
                            <Button
                                onClick={() => handleColorSelect(scheme)}
                                className={`paintThePlan__colorButton ${!scheme.color ? 'paintThePlan__colorButton--noColor' : ''}`}
                                style={{
                                    backgroundColor: scheme.color || 'transparent',
                                    border: currentColor === scheme.color
                                        ? '2px solid #1976d2'
                                        : '1px solid #e0e0e0'
                                }}
                            >
                                {!scheme.color && <FormatColorResetIcon fontSize="small" />}
                            </Button>
                        </Tooltip>
                    ))}
                </Box>
            </Popover>
        </Box>
    );
};

export default PaintThePlan;