// frontend/src/redux/reducers/salesbudget/index.js
import { combineReducers } from 'redux';
import salesBudgetReducer from './salesBudgetReducer';

const rootReducer = combineReducers({
  salesBudget: salesBudgetReducer,
  
});

export default rootReducer;
