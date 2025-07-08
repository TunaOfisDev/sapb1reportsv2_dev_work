// frontend/src/redux/reducers/salesbudgetv2/index.js
import { combineReducers } from 'redux';
import salesBudgetReducerv2 from './salesBudgetReducerv2';

// Burada kombine edilen reducer'ların isimlerini değiştiriyoruz
// 'salesBudget' yerine 'salesBudgetv2' kullanarak isim çakışmasını önlüyoruz
const rootReducer = combineReducers({
  salesBudgetv2: salesBudgetReducerv2,
});

export default rootReducer;