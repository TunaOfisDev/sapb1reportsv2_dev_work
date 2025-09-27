// frontend/src/components/ShipWeekPlanner/components/GeneralSearch.js
import React, { useState } from 'react';
import { TextField, Button } from '@mui/material';
import '../css/GeneralSearch.css'; // CSS dosyasını import ettiğinizden emin olun

const GeneralSearch = ({ onSearch }) => {
    const [query, setQuery] = useState('');

    const handleSearchClick = () => {
        onSearch(query);
    };

    return (
        <div className="general-search">
            <TextField
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="Arama yapın..."
                variant="outlined"
                size="small"
            />
            <Button 
                variant="contained" 
                color="primary" 
                onClick={handleSearchClick} 
                style={{ marginLeft: '10px' }}
            >
                Ara
            </Button>
        </div>
    );
};

export default GeneralSearch;
