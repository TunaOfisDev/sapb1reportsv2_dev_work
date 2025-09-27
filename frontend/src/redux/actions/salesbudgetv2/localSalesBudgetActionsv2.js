// frontend/src/redux/actions/salesbudgetv2/localSalesBudgetActionsv2.js
import {
  FETCH_LOCAL_SALES_BUDGET_REQUEST,
  FETCH_LOCAL_SALES_BUDGET_SUCCESS,
  FETCH_LOCAL_SALES_BUDGET_FAILURE
} from './actionTypesv2';
import salesbudgetv2 from '../../../api/salesbudgetv2';

export const fetchLocalSalesBudgetsv2 = () => {
  return async (dispatch) => {
    dispatch({ type: FETCH_LOCAL_SALES_BUDGET_REQUEST });
    try {
      // salesbudgetv2 API servisini kullanarak verileri çek
      const data = await salesbudgetv2.getsalesbudgetv2s();
      
      dispatch({
        type: FETCH_LOCAL_SALES_BUDGET_SUCCESS,
        payload: data || [] // data undefined veya null ise boş dizi kullan
      });
      
      return data; // Başarılı veriyi döndür
    } catch (error) {
      console.error('Yerel bütçe verileri yüklenirken bir hata meydana geldi:', error);
      dispatch({
        type: FETCH_LOCAL_SALES_BUDGET_FAILURE,
        payload: error.message
      });
      
      throw error; // Hatayı yukarıya fırlat
    }
  };
};

export default fetchLocalSalesBudgetsv2;