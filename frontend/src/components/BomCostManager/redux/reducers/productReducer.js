// frontend/src/components/BomCostManager/redux/reducers/productReducer.js

import {
    FETCH_PRODUCTS_REQUEST,
    FETCH_PRODUCTS_SUCCESS,
    FETCH_PRODUCTS_FAILURE,
    FETCH_PRODUCT_DETAILS_REQUEST,
    FETCH_PRODUCT_DETAILS_SUCCESS,
    FETCH_PRODUCT_DETAILS_FAILURE
} from '../types';

const initialState = {
    products: [],
    productDetails: null,
    loading: false,
    error: null,
};

/**
 * BOM ürünlerinin Redux state yönetimi için reducer fonksiyonu.
 */
const productReducer = (state = initialState, action) => {
    switch (action.type) {
        case FETCH_PRODUCTS_REQUEST:
            return { ...state, loading: true, error: null };
        case FETCH_PRODUCTS_SUCCESS:
            return { ...state, loading: false, products: action.payload };
        case FETCH_PRODUCTS_FAILURE:
            return { ...state, loading: false, error: action.payload };
        
        case FETCH_PRODUCT_DETAILS_REQUEST:
            return { ...state, loading: true, productDetails: null, error: null };
        case FETCH_PRODUCT_DETAILS_SUCCESS:
            return { ...state, loading: false, productDetails: action.payload };
        case FETCH_PRODUCT_DETAILS_FAILURE:
            return { ...state, loading: false, error: action.payload };
        
        default:
            return state;
    }
};

export default productReducer;
