// frontend/src/redux/actions/salesbudgetv2/hanaSalesBudgetActions.js
import {
  FETCH_HANA_SALES_BUDGET_REQUEST,
  FETCH_HANA_SALES_BUDGET_SUCCESS,
  FETCH_HANA_SALES_BUDGET_FAILURE
} from './actionTypesv2';
import axiosInstance from '../../../api/axiosconfig';

// HANA bütçe verilerini çekmek için asenkron eylem
export const fetchHanaSalesBudgetsv2 = () => {
  return async (dispatch) => {
    dispatch({ type: FETCH_HANA_SALES_BUDGET_REQUEST });
    try {
      const response = await axiosInstance.get('salesbudgetv2/fetch-hana-data/');
      dispatch({
        type: FETCH_HANA_SALES_BUDGET_SUCCESS,
        payload: response.data.results  // API'den gelen 'results' anahtarını payload olarak gönder
      });
    } catch (error) {
      console.error('HANA bütçe verileri yüklenirken bir hata meydana geldi:', error);
      dispatch({
        type: FETCH_HANA_SALES_BUDGET_FAILURE,
        payload: error.message  // Hata mesajını payload olarak gönder
      });
    }
  };
};

export default fetchHanaSalesBudgetsv2;
