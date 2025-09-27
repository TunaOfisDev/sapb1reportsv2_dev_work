// frontend/src/components/BomCostManager/redux/bomcoststore.js

import { configureStore } from '@reduxjs/toolkit';
import rootReducer from './reducers/rootReducer';

/**
 * Redux store yapılandırması.
 */
const store = configureStore({
    reducer: rootReducer,
    devTools: process.env.NODE_ENV !== 'production',
});

export default store;
