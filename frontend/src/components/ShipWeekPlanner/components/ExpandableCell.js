// frontend/src/components/ShipWeekPlanner/components/ExpandableCell.js
import React, { useState } from 'react';
import { TextField, Tooltip } from '@mui/material';

const ExpandableCell = ({ value, onChange, disabled }) => {
    const [isHovered, setIsHovered] = useState(false);

    return (
        <div
            className="expandable-cell-container"
            onMouseEnter={() => setIsHovered(true)}
            onMouseLeave={() => setIsHovered(false)}
        >
            <Tooltip
                open={isHovered && value?.length > 0}
                title={value || ''}
                placement="right-start"
                arrow
            >
                <TextField
                    value={value || ''}
                    onChange={onChange}
                    disabled={disabled}
                    fullWidth
                    size="small"
                    variant="standard"
                    InputProps={{
                        disableUnderline: !isHovered,
                        style: {
                            fontSize: '0.875rem',
                            padding: '0'
                        }
                    }}
                    sx={{
                        '& .MuiInputBase-input': {
                            padding: '4px 8px',
                        }
                    }}
                />
            </Tooltip>
        </div>
    );
};

export default ExpandableCell;