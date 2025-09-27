// frontend\src\components\ProductConfig\common\PCLoadingTransition.js
import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import '../css/PCLoadingTransition.css';

const PCLoadingTransition = ({ isLoading, children }) => {
    return (
        <div className="pc-loading-transition">
            <AnimatePresence mode="wait">
                {isLoading ? (
                    <motion.div
                        key="loading"
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        exit={{ opacity: 0 }}
                        transition={{ duration: 0.5 }}
                        className="pc-loading-transition__overlay"
                    >
                        <div className="pc-loading-transition__content">
                            <div className="pc-loading-transition__spinner" />
                            <span className="pc-loading-transition__text">Yükleniyor...</span>
                        </div>
                    </motion.div>
                ) : (
                    <motion.div
                        key="content"
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        exit={{ opacity: 0 }}
                        transition={{ duration: 0.5 }}
                    >
                        {children}
                    </motion.div>
                )}
            </AnimatePresence>
        </div>
    );
};

export default PCLoadingTransition;
