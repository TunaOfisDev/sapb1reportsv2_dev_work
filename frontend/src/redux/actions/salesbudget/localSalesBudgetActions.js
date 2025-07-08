// frontend/src/redux/actions/salesbudget/localSalesBudgetActions.js
import {
    FETCH_LOCAL_SALES_BUDGET_REQUEST,
    FETCH_LOCAL_SALES_BUDGET_SUCCESS,
    FETCH_LOCAL_SALES_BUDGET_FAILURE
  } from './actionTypes';
  import axiosInstance from '../../../api/axiosconfig';
  
  export const fetchLocalSalesBudgets = () => {
    return async (dispatch) => {
      dispatch({ type: FETCH_LOCAL_SALES_BUDGET_REQUEST });
      try {
        const response = await axiosInstance.get('salesbudget/budgets/');
        dispatch({
          type: FETCH_LOCAL_SALES_BUDGET_SUCCESS,
          payload: response.data.results
        });
      } catch (error) {
        console.error('Yerel bütçe verileri yüklenirken bir hata meydana geldi:', error);
        dispatch({
          type: FETCH_LOCAL_SALES_BUDGET_FAILURE,
          payload: error.message
        });
      }
    };
  };
  
  export default fetchLocalSalesBudgets;
  