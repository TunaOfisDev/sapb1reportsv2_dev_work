// frontend/src/components/BomCostManager/redux/actions/productActions.js

import {
    FETCH_PRODUCTS_REQUEST,
    FETCH_PRODUCTS_SUCCESS,
    FETCH_PRODUCTS_FAILURE,
    FETCH_PRODUCT_DETAILS_REQUEST,
    FETCH_PRODUCT_DETAILS_SUCCESS,
    FETCH_PRODUCT_DETAILS_FAILURE
} from '../types';
import {
    fetchAllProducts,
    fetchProductDetails
} from '../../services/bcm_productApi';

/**
 * Tüm BOM ürünlerini getirmek için Redux action'ı.
 */
export const fetchProducts = () => async (dispatch) => {
    dispatch({ type: FETCH_PRODUCTS_REQUEST });
    try {
        const data = await fetchAllProducts();
        dispatch({ type: FETCH_PRODUCTS_SUCCESS, payload: data });
    } catch (error) {
        dispatch({ type: FETCH_PRODUCTS_FAILURE, payload: error.message });
    }
};

/**
 * Belirli bir BOM ürününün detaylarını getirmek için Redux action'ı.
 * @param {string} itemCode - Ürün kodu.
 */
export const fetchProductDetailsAction = (itemCode) => async (dispatch) => {
    dispatch({ type: FETCH_PRODUCT_DETAILS_REQUEST });
    try {
        const data = await fetchProductDetails(itemCode);
        dispatch({ type: FETCH_PRODUCT_DETAILS_SUCCESS, payload: data });
    } catch (error) {
        dispatch({ type: FETCH_PRODUCT_DETAILS_FAILURE, payload: error.message });
    }
};
