// frontend/src/components/BomCostManager/redux/reducers/bomCostReducer.js

import {
    FETCH_BOM_COST_REQUEST,
    FETCH_BOM_COST_SUCCESS,
    FETCH_BOM_COST_FAILURE,
    UPDATE_BOM_COMPONENT_REQUEST,
    UPDATE_BOM_COMPONENT_SUCCESS,
    UPDATE_BOM_COMPONENT_FAILURE
} from '../types';

const initialState = {
    bomComponents: [],
    loading: false,
    error: null,
};

/**
 * BOM bileşenlerinin Redux state yönetimi için reducer fonksiyonu.
 */
const bomCostReducer = (state = initialState, action) => {
    switch (action.type) {
        case FETCH_BOM_COST_REQUEST:
            return { ...state, loading: true, error: null };
        case FETCH_BOM_COST_SUCCESS:
            return { ...state, loading: false, bomComponents: action.payload };
        case FETCH_BOM_COST_FAILURE:
            return { ...state, loading: false, error: action.payload };
        
        case UPDATE_BOM_COMPONENT_REQUEST:
            return { ...state, loading: true };
        case UPDATE_BOM_COMPONENT_SUCCESS:
            return {
                ...state,
                loading: false,
                bomComponents: state.bomComponents.map(component => 
                    component.id === action.payload.id ? action.payload : component
                )
            };
        case UPDATE_BOM_COMPONENT_FAILURE:
            return { ...state, loading: false, error: action.payload };
        
        default:
            return state;
    }
};

export default bomCostReducer;
