// frontend/src/components/ShipWeekPlanner/components/CopyToForm.js
import React from 'react';
import { Button, Tooltip } from '@mui/material';
import ContentCopyIcon from '@mui/icons-material/ContentCopy';

const fieldsToCopy = [
    'order_number',
    'customer_name',
    'order_date',
    'shipment_date',
    'sales_person',
    'shipment_details',
    'shipment_notes'
];

const CopyToForm = ({ rowData, onCopy }) => {
    const handleCopy = () => {
        // Seçilen alanları kopyala
        const copiedData = {};
        
        fieldsToCopy.forEach(field => {
            if (field.includes('date') && rowData[field]) {
                // Tarih alanları için özel işlem
                copiedData[field] = new Date(rowData[field]);
            } else {
                copiedData[field] = rowData[field];
            }
        });

        // Yeni satır için bazı alanları sıfırla/değiştir
        const newRowData = {
            ...copiedData,
            id: 'new',
            order_status: 'Acik',
            order_number: `${copiedData.order_number}-COPY`,
            planned_date_real: null,
            planned_date_week: null,
            planned_date_mirror: null,
            planned_dates: []
        };

        onCopy(newRowData);
    };

    return (
        <Tooltip title="Satırı Kopyala">
            <Button
                variant="outlined"
                color="primary"
                size="small"
                onClick={handleCopy}
                sx={{
                    minWidth: '40px',
                    padding: '4px',
                    marginLeft: '8px',
                    '& .MuiButton-startIcon': {
                        margin: 0
                    }
                }}
                startIcon={<ContentCopyIcon />}
            />
        </Tooltip>
    );
};

export default CopyToForm;