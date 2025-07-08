// frontend/src/redux/reducers/salesbudgetv2/salesBudgetReducerv2.js
import {
  FETCH_LOCAL_SALES_BUDGET_REQUEST,
  FETCH_LOCAL_SALES_BUDGET_SUCCESS,
  FETCH_LOCAL_SALES_BUDGET_FAILURE,
  FETCH_HANA_SALES_BUDGET_REQUEST,
  FETCH_HANA_SALES_BUDGET_SUCCESS,
  FETCH_HANA_SALES_BUDGET_FAILURE
} from '../../actions/salesbudgetv2/actionTypesv2';

const initialState = {
  loading: false,
  salesBudgets: [],
  error: null
};

const salesBudgetReducerv2 = (state = initialState, action) => {
  switch (action.type) {
    // Veri çekme işlemi başladığında loading durumunu true yap
    case FETCH_LOCAL_SALES_BUDGET_REQUEST:
    case FETCH_HANA_SALES_BUDGET_REQUEST:
      return {
        ...state,
        loading: true,
        error: null
      };
    
    // Yerel veriler başarıyla yüklendiğinde
    case FETCH_LOCAL_SALES_BUDGET_SUCCESS:
      return {
        ...state,
        loading: false,
        salesBudgets: action.payload || [],
        error: null
      };
    
    // HANA verileri başarıyla yüklendiğinde
    // Not: HANA verileri de aynı salesBudgets dizisinde saklanıyor,
    // böylece hanaSalesBudgets ayrı tutmaya gerek kalmıyor
    case FETCH_HANA_SALES_BUDGET_SUCCESS:
      return {
        ...state,
        loading: false,
        salesBudgets: action.payload || [],
        error: null
      };
    
    // Hata durumunda
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

export default salesBudgetReducerv2;