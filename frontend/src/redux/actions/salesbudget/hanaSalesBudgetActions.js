// frontend/src/redux/actions/salesbudget/hanaSalesBudgetActions.js
import {
  FETCH_HANA_SALES_BUDGET_REQUEST,
  FETCH_HANA_SALES_BUDGET_SUCCESS,
  FETCH_HANA_SALES_BUDGET_FAILURE
} from './actionTypes';
import axiosInstance from '../../../api/axiosconfig';

// HANA bütçe verilerini çekmek için asenkron eylem
export const fetchHanaSalesBudgets = () => {
  return async (dispatch) => {
    dispatch({ type: FETCH_HANA_SALES_BUDGET_REQUEST });
    try {
      const response = await axiosInstance.get('salesbudget/fetch-hana-data/');
      dispatch({
        type: FETCH_HANA_SALES_BUDGET_SUCCESS,
        payload: response.data.results || []  // API'den gelen 'results' anahtarını payload olarak gönder, yoksa boş dizi
      });
      return response.data;
    } catch (error) {
      console.error('HANA bütçe verileri yüklenirken bir hata meydana geldi:', error);
      dispatch({
        type: FETCH_HANA_SALES_BUDGET_FAILURE,
        payload: error.message  // Hata mesajını payload olarak gönder
      });
      throw error; // Hatayı yukarıya fırlat, böylece çağıran fonksiyon hata durumunu yakalayabilir
    }
  };
};

export default fetchHanaSalesBudgets;