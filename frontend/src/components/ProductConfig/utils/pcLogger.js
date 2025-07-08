// frontend/src/components/ProductConfig/utils/pcLogger.js

const logLevel = process.env.REACT_APP_LOG_LEVEL || 'none';

const levels = {
    none: 0,
    error: 1,
    warn: 2,
    info: 3,
    log: 4,
};

const pcLogger = {
    log: (...args) => {
        if (levels[logLevel] >= levels.log) {
            console.log('[LOG]', ...args);
        }
    },
    warn: (...args) => {
        if (levels[logLevel] >= levels.warn) {
            console.warn('[WARN]', ...args);
        }
    },
    error: (...args) => {
        if (levels[logLevel] >= levels.error) {
            console.error('[ERROR]', ...args);
        }
    },
    info: (...args) => {
        if (levels[logLevel] >= levels.info) {
            console.info('[INFO]', ...args);
        }
    },
};

export default pcLogger;
