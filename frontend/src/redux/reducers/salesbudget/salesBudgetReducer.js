// frontend/src/redux/reducers/salesbudget/salesBudgetReducer.js
import {
  FETCH_LOCAL_SALES_BUDGET_REQUEST,
  FETCH_LOCAL_SALES_BUDGET_SUCCESS,
  FETCH_LOCAL_SALES_BUDGET_FAILURE,
  FETCH_HANA_SALES_BUDGET_REQUEST,
  FETCH_HANA_SALES_BUDGET_SUCCESS,
  FETCH_HANA_SALES_BUDGET_FAILURE
} from '../../actions/salesbudget/actionTypes';

const initialState = {
  loading: false,
  salesBudgets: [],
  hanaSalesBudgets: [], // HANA verileri için eklenen yeni state
  error: null
};

const salesBudgetReducer = (state = initialState, action) => {
  switch (action.type) {
    case FETCH_LOCAL_SALES_BUDGET_REQUEST:
    case FETCH_HANA_SALES_BUDGET_REQUEST:
      return {
        ...state,
        loading: true
      };
    case FETCH_LOCAL_SALES_BUDGET_SUCCESS:
      return {
        ...state,
        loading: false,
        salesBudgets: action.payload,
        error: null
      };
    case FETCH_HANA_SALES_BUDGET_SUCCESS:
      return {
        ...state,
        loading: false,
        hanaSalesBudgets: action.payload,
        error: null
      };
    case FETCH_LOCAL_SALES_BUDGET_FAILURE:
    case FETCH_HANA_SALES_BUDGET_FAILURE:
      return {
        ...state,
        loading: false,
        error: action.payload
      };
    default:
      return state;
  }
};

export default salesBudgetReducer;
