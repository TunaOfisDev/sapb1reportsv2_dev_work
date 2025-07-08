// frontend/src/components/ProductConfig/common/PCForwardButton.js
import React from 'react';
import PropTypes from 'prop-types';
import { motion } from 'framer-motion';
import '../css/PCForwardButton.css';

const PCForwardButton = ({ isLoading = false, onClick, disabled = false, children }) => {
    return (
        <motion.button
            className={`pc-forward-button ${isLoading ? 'loading' : ''}`}
            onClick={onClick}
            disabled={disabled || isLoading}
            whileTap={{ scale: 0.95 }}
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.3 }}
        >
            {isLoading ? (
                <div className="spinner" />
            ) : (
                children
            )}
        </motion.button>
    );
};

PCForwardButton.propTypes = {
    isLoading: PropTypes.bool,
    onClick: PropTypes.func.isRequired,
    disabled: PropTypes.bool,
    children: PropTypes.node.isRequired,
};

export default PCForwardButton;
