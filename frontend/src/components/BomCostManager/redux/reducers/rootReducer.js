// frontend/src/components/BomCostManager/redux/reducers/rootReducer.js

import { combineReducers } from 'redux';
import bomCostReducer from './bomCostReducer';
import productReducer from './productReducer';

/**
 * Tüm reducer'ları birleştiren root reducer.
 */
const rootReducer = combineReducers({
    bomCost: bomCostReducer,
    product: productReducer,
});

export default rootReducer;
